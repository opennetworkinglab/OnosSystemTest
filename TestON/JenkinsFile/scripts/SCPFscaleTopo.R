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

    print( paste( "Usage: Rscript SCPFgraphGenerator",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<directory-to-save-graphs>",
                                  sep=" ") )

    quit( status = 1 )  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

outputFile <- paste( args[ save_directory ],
                     args[ test_name ],
                     "_",
                     args[ branch_name ],
                     "_graph.jpg",
                     sep="" )

chartTitle <- "Scale Topology Latency Test"

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

# --------------------------
# Scale Topology SQL Command
# --------------------------

print( "Generating Scale Topology SQL Command" )

command <- paste( "SELECT * FROM scale_topo_latency_details WHERE branch = '",
                  args[ branch_name ],
                  "' AND date IN ( SELECT MAX( date ) FROM scale_topo_latency_details WHERE branch = '",
                  args[ branch_name ],
                  "' ) ",
                  sep = "" )

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

requiredColumns <- c( "last_role_request_to_last_topology", "last_connection_to_last_role_request", "first_connection_to_last_connection" )

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

# Parse lists into data frames.
dataFrame <- melt( avgs )
dataFrame$scale <- fileData$scale
colnames( dataFrame ) <- c( "s",
                            "type",
                            "scale")

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$type <- as.character( dataFrame$type )
dataFrame$type <- factor( dataFrame$type, levels=unique( dataFrame$type ) )
dataFrame$iterative <- seq( 1, nrow( fileData ), by = 1 )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

sum <- fileData[ 'last_role_request_to_last_topology' ] +
       fileData[ 'last_connection_to_last_role_request' ] +
       fileData[ 'first_connection_to_last_connection' ]

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
                                           y = s,
                                           fill = type ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 20 ) )   # set the default text size of the graph.
width <- 0.6  # Width of the bars.
xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$scale )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (s)" )
fillLabel <- labs( fill="Type" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

values <- geom_text( aes( x = dataFrame$iterative,
                          y = sum + 0.02 * max( sum ),
                          label = format( sum,
                                          big.mark = ",",
                                          scientific = FALSE ),
                          fontface = "bold" ),
                          size = 7.0 )

wrapLegend <- guides( fill = guide_legend( nrow=2, byrow=TRUE ) )

title <- ggtitle( chartTitle, "" )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        values +
                        wrapLegend +
                        title

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph." )

barGraphFormat <- geom_bar( stat = "identity", width = width )

result <- fundamentalGraphData +
          barGraphFormat

# -----------------------
# Exporting Graph to File
# -----------------------

print( paste( "Saving bar chart to", outputFile ) )

tryCatch( ggsave( outputFile,
                  width = imageWidth,
                  height = imageHeight,
                  dpi = imageDPI ),
          error = function( e ){
              print( "[ERROR] There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
              print( e )
              quit( status = 1 )
          }
        )

print( paste( "[SUCCESS] Successfully wrote bar chart out to", outputFile ) )
quit( status = 0 )
