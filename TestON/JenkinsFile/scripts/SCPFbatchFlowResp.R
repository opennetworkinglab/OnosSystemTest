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

# **********************************************************
# STEP 1: Data management.
# **********************************************************
database_host = 1
database_port = 2
database_u_id = 3
database_pw = 4
test_name = 5
branch_name = 6
old_flow = 7
save_directory = 8

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

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( is.na( args[ save_directory ] ) ){

    print( paste( "Usage: Rscript SCPFbatchFlowResp.R",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<using-old-flow>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    quit( status = 1 )  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

postOutputFile <- paste( args[ save_directory ],
                         args[ test_name ],
                         "_",
                         args[ branch_name ],
                         if( args[ old_flow ] == "y" ) "_OldFlow" else "",
                         "_PostGraph.jpg",
                         sep="" )

delOutputFile <- paste( args[ save_directory ],
                        args[ test_name ],
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

con <- dbConnect( dbDriver( "PostgreSQL" ),
                  dbname = "onostest",
                  host = args[ database_host ],
                  port = strtoi( args[ database_port ] ),
                  user = args[ database_u_id ],
                  password = args[ database_pw ] )

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

print( "Sending SQL command:" )
print( command )

fileData <- dbGetQuery( con, command )


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

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
xLabel <- xlab( "Build Date" )
yLabel <- ylab( "Latency (s)" )
fillLabel <- labs( fill="Type" )
colors <- scale_fill_manual( values=c( "#F77670", "#619DFA" ) )
wrapLegend <- guides( fill=guide_legend( nrow=1, byrow=TRUE ) )
barWidth <- 0.3
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size = 22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ),
                plot.subtitle = element_text( size=16, hjust=1.0 ) )

subtitle <- paste( "Last Updated: ", format( Sys.time(), format = "%b %d, %Y at %I:%M %p %Z" ), sep="" )

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

title <- labs( title = postChartTitle, subtitle = subtitle )

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

print( paste( "Saving Post bar chart to", postOutputFile ) )

tryCatch( ggsave( postOutputFile,
                  width = imageWidth,
                  height = imageHeight,
                  dpi = imageDPI ),
          error = function( e ){
              print( "[ERROR] There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
              print( e )
              quit( status = 1 )
          }
        )

print( paste( "[SUCCESS] Successfully wrote stacked bar chart out to", postOutputFile ) )

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

title <- labs( title = delChartTitle, subtitle = subtitle )

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

print( paste( "Saving Del bar chart to", delOutputFile ) )

tryCatch( ggsave( delOutputFile,
                  width = imageWidth,
                  height = imageHeight,
                  dpi = imageDPI ),
          error = function( e ){
              print( "[ERROR] There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
              print( e )
              quit( status = 1 )
          }
        )

print( paste( "[SUCCESS] Successfully wrote stacked bar chart out to", delOutputFile ) )
quit( status = 0 )
