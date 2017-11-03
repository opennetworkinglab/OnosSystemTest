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

    print( paste( "Usage: Rscript SCPFportLat",
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

con <- dbConnect( dbDriver( "PostgreSQL" ),
                  dbname = "onostest",
                  host = args[ database_host ],
                  port = strtoi( args[ database_port ] ),
                  user = args[ database_u_id ],
                  password = args[ database_pw ] )

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

print( "Sending SQL command:" )
print( command )

fileData <- dbGetQuery( con, command )

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

upAvgs <- c( fileData[ 'up_ofp_to_dev_avg' ],
             fileData[ 'up_dev_to_link_avg' ],
             fileData[ 'up_link_to_graph_avg' ] )

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

downAvgs <- c( fileData[ 'down_ofp_to_dev_avg' ],
               fileData[ 'down_dev_to_link_avg' ],
               fileData[ 'down_link_to_graph_avg' ] )

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

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
barWidth <- 1
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9 ) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
wrapLegend <- guides( fill=guide_legend( nrow=1, byrow=TRUE ) )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200
errorBarColor <- rgb( 140, 140, 140, maxColorValue=255 )

theme <- theme( plot.title=element_text( hjust = 0.5, size = 32, face='bold' ),
                legend.position="bottom",
                legend.text=element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

colors <- scale_fill_manual( values=c( "#F77670",
                                       "#619DFA",
                                       "#18BA48" ) )

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

title <- ggtitle( "Port Up Latency" )

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

print( paste( "Saving bar chart with error bars (Port Up Latency) to", errBarOutputFileUp ) )

ggsave( errBarOutputFileUp,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars (Port Up Latency) out to", errBarOutputFileUp ) )

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

title <- ggtitle( "Port Down Latency" )

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

print( paste( "Saving bar chart with error bars (Port Down Latency) to", errBarOutputFileDown ) )

ggsave( errBarOutputFileDown,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars (Port Down Latency) out to", errBarOutputFileDown ) )
