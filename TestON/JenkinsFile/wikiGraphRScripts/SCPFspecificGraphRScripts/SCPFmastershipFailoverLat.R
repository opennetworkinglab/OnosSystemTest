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
# Mastership Failover Graph (https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/SCPFmastershipFailoverLat_master_errGraph.jpg):
# Rscript SCPFspecificGraphRScripts/SCPFmastershipFailoverLat.R <url> <port> <username> <pass> SCPFmastershipFailoverLat master /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

save_directory <- 7

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

chartTitle <- "Mastership Failover Latency"

errBarOutputFile <- paste( args[ save_directory ],
                           args[ graph_title ],
                           "_",
                           args[ branch_name ],
                           "_errGraph.jpg",
                           sep="" )

stackedBarOutputFile <- paste( args[ save_directory ],
                        args[ graph_title ],
                        "_",
                        args[ branch_name ],
                        "_stackedGraph.jpg",
                        sep="" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ---------------------------------------
# Mastership Failover Latency SQL Command
# ---------------------------------------

print( "Generating Mastership Failover Latency SQL command" )

command  <- paste( "SELECT * FROM mastership_failover_tests WHERE branch = '",
                   args[ branch_name ],
                   "' AND date IN ( SELECT MAX( date ) FROM mastership_failover_tests WHERE branch = '",
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

# ------------
# Data Sorting
# ------------

print( "Combining averages into a list." )

requiredColumns <- c( "kill_deact_avg", "deact_role_avg" )

tryCatch( avgs <- c( fileData[ requiredColumns] ),
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

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing Data Frame from list." )

dataFrame <- melt( avgs )
dataFrame$scale <- fileData$scale
dataFrame$stds <- c( fileData$kill_deact_std,
                     fileData$deact_role_std )

colnames( dataFrame ) <- c( "ms",
                            "type",
                            "scale",
                            "stds" )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

sum <- fileData[ 'deact_role_avg' ] +
       fileData[ 'kill_deact_avg' ]

print( "Data Frame Results:" )
print( dataFrame )


# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# ------------------------------------
# Initialize Variables for Both Graphs
# ------------------------------------

print( "Initializing variables used in both graphs." )

defaultTextSize()
xScaleConfig <- scale_x_continuous( breaks = c( 1, 3, 5, 7, 9) )

xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill = "Type" )

barWidth <- 0.9

theme <- graphTheme()

barColors <- scale_fill_manual( values=c( webColor( "redv2" ),
                                          webColor( "light_blue" ) ) )

wrapLegend <- guides( fill=guide_legend( nrow=1, byrow=TRUE ) )

# ----------------------------------
# Error Bar Graph Generate Main Plot
# ----------------------------------

print( "Creating main plot." )

mainPlot <- ggplot( data = dataFrame, aes( x = scale,
                                           y = ms,
                                           ymin = ms,
                                           ymax = ms + stds,
                                           fill = type ) )

# ----------------------------------------------
# Error Bar Graph Fundamental Variables Assigned
# ----------------------------------------------

print( "Generating fundamental graph data for the error bar graph." )

title <- labs( title = chartTitle, subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        title +
                        wrapLegend

# -------------------------------------------
# Error Bar Graph Generating Bar Graph Format
# -------------------------------------------

print( "Generating bar graph with error bars." )

barGraphFormat <- geom_bar( stat = "identity",
                            position = position_dodge(),
                            width = barWidth )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 position = position_dodge(),
                                 color = webColor( "darkerGray" ) )

values <- geom_text( aes( x = dataFrame$scale,
                          y = dataFrame$ms + 0.02 * max( dataFrame$ms ),
                          label = format( dataFrame$ms,
                                          digits = 3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold",
                          position = position_dodge( 0.9 ) )

result <- fundamentalGraphData +
          barGraphFormat +
          barColors +
          errorBarFormat +
          values

# ---------------------------------------
# Error Bar Graph Exporting Graph to File
# ---------------------------------------

saveGraph( errBarOutputFile )

# ------------------------------------------------
# Stacked Bar Graph Fundamental Variables Assigned
# ------------------------------------------------

print( "Generating fundamental graph data for the stacked bar graph." )

title <- labs( title = chartTitle, subtitle = lastUpdatedLabel() )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        title +
                        wrapLegend

# ---------------------------------------------
# Stacked Bar Graph Generating Bar Graph Format
# ---------------------------------------------

print( "Generating stacked bar chart." )
stackedBarFormat <- geom_bar( stat = "identity",
                              width = barWidth )

values <- geom_text( aes( x = dataFrame$scale,
                          y = sum + 0.02 * max( sum ),
                          label = format( sum,
                                          digits = 3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          stackedBarFormat +
          barColors +
          title +
          values

# -----------------------------------------
# Stacked Bar Graph Exporting Graph to File
# -----------------------------------------

saveGraph( stackedBarOutputFile )
