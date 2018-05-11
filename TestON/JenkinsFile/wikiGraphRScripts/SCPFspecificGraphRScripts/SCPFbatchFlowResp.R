# Copyright 2017 Open Networking Foundation (ONF)
#
# Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
# the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
# or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
#
#     TestON is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 2 of the License, or
#     (at your option) any later version.
#
#     TestON is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with TestON.  If not, see <http://www.gnu.org/licenses/>.
#
# If you have any questions, or if you don't understand R,
# please contact Jeremy Ronquillo: j_ronquillo@u.pacific.edu
#
# Example script:
# Single Bench Flow Latency Graph with Eventually Consistent Flow Rule Store (https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/SCPFbatchFlowResp_master_OldFlow_PostGraph.jpg):
# Rscript SCPFbatchFlowResp.R <url> <port> <username> <pass> SCPFbatchFlowResp.R master y /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

old_flow <- 7
save_directory <- 8

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )    # For databases
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/saveGraph.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/fundamentalGraphData.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/initSQL.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/cliArgs.R" )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( length( args ) != save_directory ){
    usage( "SCPFbatchFlowResp.R", c( "using-old-flow" ) )
    quit( status = 1 )
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

postOutputFile <- paste( args[ save_directory ],
                         args[ graph_title ],
                         "_",
                         args[ branch_name ],
                         if( args[ old_flow ] == "y" ) "_OldFlow" else "",
                         "_PostGraph.jpg",
                         sep="" )

delOutputFile <- paste( args[ save_directory ],
                        args[ graph_title ],
                        "_",
                        args[ branch_name ],
                        if( args[ old_flow ] == "y" ) "_OldFlow" else "",
                        "_DelGraph.jpg",
                        sep="" )

postChartTitle <- paste( "Single Bench Flow Latency - Post\n",
                         "Last 3 Builds",
                         if( args[ old_flow ] == "y" ) "\nWith Eventually Consistent Flow Rule Store" else "",
                         sep = "" )
delChartTitle <- paste( "Single Bench Flow Latency - Del\n",
                        "Last 3 Builds",
                        if( args[ old_flow ] == "y" ) "\nWith Eventually Consistent Flow Rule Store" else "",
                        sep = "" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ---------------------------
# Batch Flow Resp SQL Command
# ---------------------------

print( "Generating Batch Flow Resp SQL Command" )

command <- paste( "SELECT * FROM batch_flow_tests WHERE branch='",
                  args[ branch_name ],
                  "' AND " ,
                  ( if( args[ old_flow ] == 'y' ) "" else "NOT " ) ,
                  "is_old_flow",
                  " ORDER BY date DESC LIMIT 3",
                  sep="" )

fileData <- retrieveData( con, command )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# -----------------
# Post Data Sorting
# -----------------

print( "Sorting data for Post." )

requiredColumns <- c( "posttoconfrm", "elapsepost" )

tryCatch( postAvgs <- c( fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from the data. Please check that the data and SQL command are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# -------------------------
# Post Construct Data Frame
# -------------------------

postDataFrame <- melt( postAvgs )
postDataFrame$scale <- fileData$scale
postDataFrame$date <- fileData$date
postDataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

colnames( postDataFrame ) <- c( "ms",
                                "type",
                                "scale",
                                "date",
                                "iterative" )

# Format data frame so that the data is in the same order as it appeared in the file.
postDataFrame$type <- as.character( postDataFrame$type )
postDataFrame$type <- factor( postDataFrame$type,
                              levels = unique( postDataFrame$type ) )

postDataFrame <- na.omit( postDataFrame )   # Omit any data that doesn't exist

print( "Post Data Frame Results:" )
print( postDataFrame )

# ----------------
# Del Data Sorting
# ----------------

requiredColumns <- c( "deltoconfrm", "elapsedel" )

tryCatch( delAvgs <- c( fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from the data. Please check that the data and SQL command are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )


# ------------------------
# Del Construct Data Frame
# ------------------------

delDataFrame <- melt( delAvgs )
delDataFrame$scale <- fileData$scale
delDataFrame$date <- fileData$date
delDataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

colnames( delDataFrame ) <- c( "ms",
                               "type",
                               "scale",
                               "date",
                               "iterative" )

# Format data frame so that the data is in the same order as it appeared in the file.
delDataFrame$type <- as.character( delDataFrame$type )
delDataFrame$type <- factor( delDataFrame$type,
                             levels = unique( delDataFrame$type ) )

delDataFrame <- na.omit( delDataFrame )   # Omit any data that doesn't exist

print( "Del Data Frame Results:" )
print( delDataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# ------------------------------------------
# Initializing variables used in both graphs
# ------------------------------------------

print( "Initializing variables used in both graphs." )

defaultTextSize()
xLabel <- xlab( "Build Date" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )

colors <- scale_fill_manual( values=c( webColor( "redv2" ),
                                       webColor( "light_blue" ) ) )

wrapLegend <- guides( fill=guide_legend( nrow=1, byrow=TRUE ) )

barWidth <- 0.3

theme <- graphTheme()

barGraphFormat <- geom_bar( stat = "identity",
                            width = barWidth )

# -----------------------
# Post Generate Main Plot
# -----------------------

print( "Creating main plot for Post graph." )

mainPlot <- ggplot( data = postDataFrame, aes( x = iterative,
                                               y = ms,
                                               fill = type ) )

# -----------------------------------
# Post Fundamental Variables Assigned
# -----------------------------------

print( "Generating fundamental graph data for Post graph." )

xScaleConfig <- scale_x_continuous( breaks = postDataFrame$iterative,
                                    label = postDataFrame$date )

title <- labs( title = postChartTitle, subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        wrapLegend +
                        colors +
                        title

# --------------------------------
# Post Generating Bar Graph Format
# --------------------------------

print( "Generating bar graph for Post graph." )

sum <- fileData[ 'posttoconfrm' ] +
       fileData[ 'elapsepost' ]

values <- geom_text( aes( x = postDataFrame$iterative,
                          y = sum + 0.03 * max( sum ),
                          label = format( sum,
                                          digits = 3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          values

# ----------------------------
# Post Exporting Graph to File
# ----------------------------

saveGraph( postOutputFile )

# ----------------------
# Del Generate Main Plot
# ----------------------

print( "Creating main plot for Del graph." )

mainPlot <- ggplot( data = delDataFrame, aes( x = iterative,
                                              y = ms,
                                              fill = type ) )

# ----------------------------------
# Del Fundamental Variables Assigned
# ----------------------------------

print( "Generating fundamental graph data for Del graph." )

xScaleConfig <- scale_x_continuous( breaks = delDataFrame$iterative,
                                    label = delDataFrame$date )

title <- labs( title = delChartTitle, subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        wrapLegend +
                        colors +
                        title

# -------------------------------
# Del Generating Bar Graph Format
# -------------------------------

print( "Generating bar graph for Del graph." )

sum <- fileData[ 'deltoconfrm' ] +
       fileData[ 'elapsedel' ]

values <- geom_text( aes( x = delDataFrame$iterative,
                          y = sum + 0.03 * max( sum ),
                          label = format( sum,
                                          digits = 3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          title +
          values

# ---------------------------
# Del Exporting Graph to File
# ---------------------------

saveGraph( delOutputFile )
quit( status = 0 )
