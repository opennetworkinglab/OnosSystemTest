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
    print( paste( "Usage: Rscript SCPFmastershipFailoverLat",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

        q()  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

chartTitle <- "Mastership Failover Latency"

errBarOutputFile <- paste( args[ save_directory ],
                           args[ test_name ],
                           "_",
                           args[ branch_name ],
                           "_errGraph.jpg",
                           sep="" )

stackedBarOutputFile <- paste( args[ save_directory ],
                        args[ test_name ],
                        "_",
                        args[ branch_name ],
                        "_stackedGraph.jpg",
                        sep="" )

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

print( "Combining averages into a list." )

avgs <- c( fileData[ 'kill_deact_avg' ],
           fileData[ 'deact_role_avg' ] )

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

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
xScaleConfig <- scale_x_continuous( breaks = c( 1, 3, 5, 7, 9) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill = "Type" )
barWidth <- 0.9
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face='bold' ),
                legend.position = "bottom",
                legend.text = element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

barColors <- scale_fill_manual( values=c( "#F77670",
                                       "#619DFA" ) )

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

errorBarColor <- rgb( 140, 140, 140, maxColorValue=255 )

title <- ggtitle( chartTitle )

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
                                 color = errorBarColor )

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

print( paste( "Saving bar chart with error bars to", errBarOutputFile ) )

ggsave( errBarOutputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars out to", errBarOutputFile ) )

# ------------------------------------------------
# Stacked Bar Graph Fundamental Variables Assigned
# ------------------------------------------------

print( "Generating fundamental graph data for the stacked bar graph." )

title <- ggtitle( chartTitle )

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

print( paste( "Saving stacked bar chart to", stackedBarOutputFile ) )

ggsave( stackedBarOutputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote stacked bar chart out to", stackedBarOutputFile ) )
