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

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )
database_host = 1
database_port = 2
database_u_id = 3
database_pw = 4
test_name = 5
branch_name = 6
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

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( is.na( args[ save_directory ] ) ){

    print( paste( "Usage: Rscript SCPFcbench",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    quit( status = 1 )  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

errBarOutputFile <- paste( args[ save_directory ],
                           args[ test_name ],
                           "_",
                           args[ branch_name ],
                           "_errGraph.jpg",
                           sep="" )

chartTitle <- paste( "Single-Node CBench Throughput", "Last 3 Builds", sep = "\n" )

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

# ------------------
# Cbench SQL Command
# ------------------

print( "Generating Scale Topology SQL Command" )

command <- paste( "SELECT * FROM cbench_bm_tests WHERE branch='",
                  args[ branch_name ],
                  "' ORDER BY date DESC LIMIT 3",
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

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
barWidth <- 0.3
xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$date )
xLabel <- xlab( "Build Date" )
yLabel <- ylab( "Responses / sec" )
fillLabel <- labs( fill = "Type" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200
errorBarColor <- rgb( 140,140,140, maxColorValue=255 )

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size = 18, face = "bold" ),
                legend.title = element_blank(),
                plot.subtitle = element_text( size=16, hjust=1.0 ) )

subtitle <- paste( "Last Updated: ", format( Sys.time(), format = "%b %d, %Y at %I:%M %p %Z" ), sep="" )

title <- labs( title = chartTitle, subtitle = subtitle )

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
                            fill = "#00AA13" )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 color = errorBarColor )

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

print( paste( "Saving bar chart with error bars to", errBarOutputFile ) )

tryCatch( ggsave( errBarOutputFile,
                  width = imageWidth,
                  height = imageHeight,
                  dpi = imageDPI ),
          error = function( e ){
              print( "[ERROR] There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
              print( e )
              quit( status = 1 )
          }
        )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars out to", errBarOutputFile ) )
