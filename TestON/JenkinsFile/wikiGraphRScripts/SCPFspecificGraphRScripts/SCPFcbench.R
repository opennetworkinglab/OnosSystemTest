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
# Cbench Graph (https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/SCPFcbench_master_errGraph.jpg):
# Rscript SCPFspecificGraphRScripts/SCPFcbench.R <url> <port> <username> <pass> SCPFcbench master /path/to/save/directory/

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
    usage( "SCPFcbench.R" )
    quit( status = 1 )
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

errBarOutputFile <- paste( args[ save_directory ],
                           args[ graph_title ],
                           "_",
                           args[ branch_name ],
                           "_errGraph.jpg",
                           sep="" )

chartTitle <- paste( "Single-Node CBench Throughput", "Last 3 Builds", sep = "\n" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ------------------
# Cbench SQL Command
# ------------------

print( "Generating Scale Topology SQL Command" )

command <- paste( "SELECT * FROM cbench_bm_tests WHERE branch='",
                  args[ branch_name ],
                  "' ORDER BY date DESC LIMIT 3",
                  sep="" )

fileData <- retrieveData( con, command )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

latestBuildDate <- fileData$date[1]

# ------------
# Data Sorting
# ------------

print( "Sorting data." )

requiredColumns <- c( "avg" )

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

print( "Constructing Data Frame" )

dataFrame <- melt( avgs )
dataFrame$std <- c( fileData$std )
dataFrame$date <- c( fileData$date )
dataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

colnames( dataFrame ) <- c( "ms",
                            "type",
                            "std",
                            "date",
                            "iterative" )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# ------------------
# Generate Main Plot
# ------------------

print( "Creating main plot." )

mainPlot <- ggplot( data = dataFrame, aes( x = iterative,
                                           y = ms,
                                           ymin = ms,
                                           ymax = ms + std ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

defaultTextSize()

barWidth <- 0.3

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$date )
xLabel <- xlab( "Build Date" )
yLabel <- ylab( "Responses / sec" )
fillLabel <- labs( fill = "Type" )

theme <- graphTheme()

title <- labs( title = chartTitle, subtitle = lastUpdatedLabel( latestBuildDate ) )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        title

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph with error bars." )

barGraphFormat <- geom_bar( stat = "identity",
                            position = position_dodge(),
                            width = barWidth,
                            fill = webColor( "green" ) )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 color = webColor( "darkerGray" ) )

values <- geom_text( aes( x=dataFrame$iterative,
                          y=fileData[ 'avg' ] + 0.025 * max( fileData[ 'avg' ] ),
                          label = format( fileData[ 'avg' ],
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          values

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( errBarOutputFile ) # from saveGraph.R
