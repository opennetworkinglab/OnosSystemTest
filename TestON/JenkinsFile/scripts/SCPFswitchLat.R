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

    print( paste( "Usage: Rscript SCPFswitchLat",
                            "<database-host>",
                            "<database-port>",
                            "<database-user-id>",
                            "<database-password>",
                            "<test-name>",
                            "<branch-name>",
                            "<directory-to-save-graphs>",
                            sep=" ") )

    q()  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

errBarOutputFileUp <- paste( args[ save_directory ],
                             "SCPFswitchLat_",
                             args[ branch_name ],
                             "_UpErrBarWithStack.jpg",
                             sep="" )

errBarOutputFileDown <- paste( args[ save_directory ],
                               "SCPFswitchLat_",
                               args[ branch_name ],
                               "_DownErrBarWithStack.jpg",
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

# --------------------------
# Switch Latency SQL Command
# --------------------------

print( "Generating Switch Latency SQL Command" )

command <- paste( "SELECT * FROM switch_latency_details WHERE branch = '",
                  args[ branch_name ],
                  "' AND date IN ( SELECT MAX( date ) FROM switch_latency_details WHERE branch='",
                  args[ branch_name ],
                  "' )",
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

# -------------------------------
# Switch Up Averages Data Sorting
# -------------------------------

print( "Sorting data for Switch Up Averages." )

upAvgs <- c( fileData[ 'up_device_to_graph_avg' ],
             fileData[ 'role_reply_to_device_avg' ],
             fileData[ 'role_request_to_role_reply_avg' ],
             fileData[ 'feature_reply_to_role_request_avg' ],
             fileData[ 'tcp_to_feature_reply_avg' ] )

# ------------------------------
# Switch Up Construct Data Frame
# ------------------------------

print( "Constructing Switch Up data frame." )

upAvgsData <- melt( upAvgs )
upAvgsData$scale <- fileData$scale
upAvgsData$up_std <- fileData$up_std
upAvgsData <- na.omit( upAvgsData )

colnames( upAvgsData ) <- c( "ms",
                             "type",
                             "scale",
                             "stds" )

upAvgsData$type <- as.character( upAvgsData$type )
upAvgsData$type <- factor( upAvgsData$type, levels=unique( upAvgsData$type ) )

sumOfUpAvgs <- fileData[ 'up_device_to_graph_avg' ] +
               fileData[ 'role_reply_to_device_avg' ] +
               fileData[ 'role_request_to_role_reply_avg' ] +
               fileData[ 'feature_reply_to_role_request_avg' ] +
               fileData[ 'tcp_to_feature_reply_avg' ]

print( "Up Averages Results:" )
print( upAvgsData )

# ---------------------------------
# Switch Down Averages Data Sorting
# ---------------------------------

print( "Sorting data for Switch Down Averages." )

downAvgs <- c( fileData[ 'down_device_to_graph_avg' ],
               fileData[ 'ack_to_device_avg' ],
               fileData[ 'fin_ack_to_ack_avg' ] )

# --------------------------------
# Switch Down Construct Data Frame
# --------------------------------

print( "Constructing Switch Down data frame." )

downAvgsData <- melt( downAvgs )
downAvgsData$scale <- fileData$scale
downAvgsData$down_std <- fileData$down_std

colnames( downAvgsData ) <- c( "ms",
                               "type",
                               "scale",
                               "stds" )

downAvgsData$type <- as.character( downAvgsData$type )
downAvgsData$type <- factor( downAvgsData$type, levels=unique( downAvgsData$type ) )

downAvgsData <- na.omit( downAvgsData )

sumOfDownAvgs <- fileData[ 'down_device_to_graph_avg' ] +
                 fileData[ 'ack_to_device_avg' ] +
                 fileData[ 'fin_ack_to_ack_avg' ]

print( "Down Averages Results:" )
print( downAvgsData )

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

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graphs
xScaleConfig <- scale_x_continuous( breaks = c( 1, 3, 5, 7, 9 ) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200
errorBarColor <- rgb( 140, 140, 140, maxColorValue = 255 )
barWidth <- 1

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size = 22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

# ----------------------------
# Switch Up Generate Main Plot
# ----------------------------

print( "Creating main plot (Switch Up Latency)." )

mainPlot <- ggplot( data = upAvgsData, aes( x = scale,
                                            y = ms,
                                            fill = type,
                                            ymin = fileData[ 'up_end_to_end_avg' ],
                                            ymax = fileData[ 'up_end_to_end_avg' ] + stds ) )

# ----------------------------------------
# Switch Up Fundamental Variables Assigned
# ----------------------------------------

print( "Generating fundamental graph data (Switch Up Latency)." )

title <- ggtitle( "Switch Up Latency" )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        theme +
                        title

# -------------------------------------
# Switch Up Generating Bar Graph Format
# -------------------------------------

print( "Generating bar graph with error bars (Switch Up Latency)." )

barGraphFormat <- geom_bar( stat = "identity", width = barWidth )
errorBarFormat <- geom_errorbar( width = barWidth, color = errorBarColor )

barGraphValues <- geom_text( aes( x = upAvgsData$scale,
                                  y = sumOfUpAvgs + 0.04 * max( sumOfUpAvgs ),
                                  label = format( sumOfUpAvgs,
                                                  digits = 3,
                                                  big.mark = ",",
                                                  scientific = FALSE ) ),
                                  size = 7.0,
                                  fontface = "bold" )

wrapLegend <- guides( fill = guide_legend( nrow = 2, byrow = TRUE ) )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          barGraphValues +
          wrapLegend

# ---------------------------------
# Switch Up Exporting Graph to File
# ---------------------------------

print( paste( "Saving bar chart with error bars (Switch Up Latency) to", errBarOutputFileUp ) )

ggsave( errBarOutputFileUp,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars (Switch Up Latency) out to", errBarOutputFileUp ) )

# ------------------------------
# Switch Down Generate Main Plot
# ------------------------------

print( "Creating main plot (Switch Down Latency)." )

mainPlot <- ggplot( data = downAvgsData, aes( x = scale,
                                              y = ms,
                                              fill = type,
                                              ymin = fileData[ 'down_end_to_end_avg' ],
                                              ymax = fileData[ 'down_end_to_end_avg' ] + stds ) )

# ------------------------------------------
# Switch Down Fundamental Variables Assigned
# ------------------------------------------

print( "Generating fundamental graph data (Switch Down Latency)." )

colors <- scale_fill_manual( values=c( "#F77670",       # Red
                                       "#619DFA",       # Blue
                                       "#18BA48" ) )    # Green

title <- ggtitle( "Switch Down Latency" )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        theme +
                        title

# ---------------------------------------
# Switch Down Generating Bar Graph Format
# ---------------------------------------

print( "Generating bar graph with error bars (Switch Down Latency)." )
barGraphFormat <- geom_bar( stat = "identity", width = barWidth )
errorBarFormat <- geom_errorbar( width = barWidth, color = errorBarColor )

barGraphValues <- geom_text( aes( x = downAvgsData$scale,
                                  y = sumOfDownAvgs + 0.04 * max( sumOfDownAvgs ),
                                  label = format( sumOfDownAvgs,
                                                  digits = 3,
                                                  big.mark = ",",
                                                  scientific = FALSE ) ),
                                  size = 7.0,
                                  fontface = "bold" )

wrapLegend <- guides( fill = guide_legend( nrow = 1, byrow = TRUE ) )

result <- fundamentalGraphData +
          barGraphFormat +
          colors +
          errorBarFormat +
          barGraphValues +
          wrapLegend

# -----------------------------------
# Switch Down Exporting Graph to File
# -----------------------------------

print( paste( "Saving bar chart with error bars (Switch Down Latency) to", errBarOutputFileDown ) )

ggsave( errBarOutputFileDown,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars (Switch Down Latency) out to", errBarOutputFileDown ) )
