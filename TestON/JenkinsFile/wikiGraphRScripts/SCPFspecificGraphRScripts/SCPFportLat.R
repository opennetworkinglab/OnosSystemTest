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
# Example script:
# Port Latency Graph (https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/SCPFportLat_master_UpErrBarWithStack.jpg):
# Rscript SCPFportLat.R <url> <port> <username> <pass> SCPFmastershipFailoverLat master /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

save_directory = 7

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
    usage( "SCPFmastershipFailoverLat.R" )
    quit( status = 1 )
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )
errBarOutputFileUp <- paste( args[ save_directory ],
                             "SCPFportLat_",
                             args[ branch_name ],
                             "_UpErrBarWithStack.jpg",
                             sep = "" )

errBarOutputFileDown <- paste( args[ save_directory ],
                             "SCPFportLat_",
                             args[ branch_name ],
                             "_DownErrBarWithStack.jpg",
                             sep = "" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ------------------------
# Port Latency SQL Command
# ------------------------

print( "Generating Port Latency SQL Command" )

command <- paste( "SELECT * FROM port_latency_details WHERE branch = '",
                  args[ branch_name ],
                  "' AND date IN ( SELECT MAX( date ) FROM port_latency_details WHERE branch = '",
                  args[ branch_name ],
                  "' ) ",
                  sep = "" )

fileData <- retrieveData( con, command )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# -----------------------------
# Port Up Averages Data Sorting
# -----------------------------

print( "Sorting data for Port Up Averages." )

requiredColumns <- c( "up_ofp_to_dev_avg", "up_dev_to_link_avg", "up_link_to_graph_avg" )

tryCatch( upAvgs <- c( fileData[ requiredColumns] ),
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

# ----------------------------
# Port Up Construct Data Frame
# ----------------------------

print( "Constructing Port Up data frame." )

upAvgsDataFrame <- melt( upAvgs )
upAvgsDataFrame$scale <- fileData$scale
upAvgsDataFrame$up_std <- fileData$up_std

colnames( upAvgsDataFrame ) <- c( "ms",
                             "type",
                             "scale",
                             "stds" )

upAvgsDataFrame <- na.omit( upAvgsDataFrame )

upAvgsDataFrame$type <- as.character( upAvgsDataFrame$type )
upAvgsDataFrame$type <- factor( upAvgsDataFrame$type, levels=unique( upAvgsDataFrame$type ) )

sumOfUpAvgs <- fileData[ 'up_ofp_to_dev_avg' ] +
               fileData[ 'up_dev_to_link_avg' ] +
               fileData[ 'up_link_to_graph_avg' ]

print( "Up Averages Results:" )
print( upAvgsDataFrame )

# -------------------------------
# Port Down Averages Data Sorting
# -------------------------------

print( "Sorting data for Port Down Averages." )

requiredColumns <- c( "down_ofp_to_dev_avg", "down_dev_to_link_avg", "down_link_to_graph_avg" )

tryCatch( downAvgs <- c( fileData[ requiredColumns] ),
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

# ------------------------------
# Port Down Construct Data Frame
# ------------------------------

print( "Constructing Port Down data frame." )

downAvgsDataFrame <- melt( downAvgs )
downAvgsDataFrame$scale <- fileData$scale
downAvgsDataFrame$down_std <- fileData$down_std

colnames( downAvgsDataFrame ) <- c( "ms",
                               "type",
                               "scale",
                               "stds" )

downAvgsDataFrame <- na.omit( downAvgsDataFrame )

downAvgsDataFrame$type <- as.character( downAvgsDataFrame$type )
downAvgsDataFrame$type <- factor( downAvgsDataFrame$type, levels=unique( downAvgsDataFrame$type ) )

sumOfDownAvgs <- fileData[ 'down_ofp_to_dev_avg' ] +
                 fileData[ 'down_dev_to_link_avg' ] +
                 fileData[ 'down_link_to_graph_avg' ]

print( "Down Averages Results:" )
print( downAvgsDataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# ------------------------------------
# Initialize Variables For Both Graphs
# ------------------------------------

print( "Initializing variables used in both graphs." )

defaultTextSize()
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9 ) )

xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )

barWidth <- 1

wrapLegend <- guides( fill=guide_legend( nrow=1, byrow=TRUE ) )

theme <- graphTheme()

subtitle <- lastUpdatedLabel()

colors <- scale_fill_manual( values=c( webColor( "redv2" ),
                                       webColor( "light_blue" ),
                                       webColor( "green" ) ) )

errorBarColor <- webColor( "darkerGray" )

# --------------------------
# Port Up Generate Main Plot
# --------------------------

print( "Generating main plot (Port Up Latency)." )

mainPlot <- ggplot( data = upAvgsDataFrame, aes( x = scale,
                                            y = ms,
                                            fill = type,
                                            ymin = fileData[ 'up_end_to_end_avg' ],
                                            ymax = fileData[ 'up_end_to_end_avg' ] + stds ) )

# --------------------------------------
# Port Up Fundamental Variables Assigned
# --------------------------------------

print( "Generating fundamental graph data (Port Up Latency)." )

title <- labs( title = "Port Up Latency", subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        wrapLegend +
                        title +
                        colors

# -----------------------------------
# Port Up Generating Bar Graph Format
# -----------------------------------

print( "Generating bar graph with error bars (Port Up Latency)." )

barGraphFormat <- geom_bar( stat = "identity",
                            width = barWidth )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 color = errorBarColor )

values <- geom_text( aes( x = upAvgsDataFrame$scale,
                          y = sumOfUpAvgs + 0.03 * max( sumOfUpAvgs ),
                          label = format( sumOfUpAvgs,
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          values

# -------------------------------
# Port Up Exporting Graph to File
# -------------------------------

saveGraph( errBarOutputFileUp )

# ----------------------------
# Port Down Generate Main Plot
# ----------------------------

print( "Generating main plot (Port Down Latency)." )

mainPlot <- ggplot( data = downAvgsDataFrame, aes( x = scale,
                                              y = ms,
                                              fill = type,
                                              ymin = fileData[ 'down_end_to_end_avg' ],
                                              ymax = fileData[ 'down_end_to_end_avg' ] + stds ) )

# ----------------------------------------
# Port Down Fundamental Variables Assigned
# ----------------------------------------

print( "Generating fundamental graph data (Port Down Latency)." )

title <- labs( title = "Port Down Latency", subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        wrapLegend +
                        title +
                        colors

# -------------------------------------
# Port Down Generating Bar Graph Format
# -------------------------------------

print( "Generating bar graph with error bars (Port Down Latency)." )

barGraphFormat <- geom_bar( stat = "identity",
                            width = barWidth )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 color = errorBarColor )

values <- geom_text( aes( x = downAvgsDataFrame$scale,
                          y = sumOfDownAvgs + 0.03 * max( sumOfDownAvgs ),
                          label = format( sumOfDownAvgs,
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          values

# ---------------------------------
# Port Down Exporting Graph to File
# ---------------------------------

saveGraph( errBarOutputFileDown )
quit( status = 0 )
