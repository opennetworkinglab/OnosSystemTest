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

if ( is.na( args[ 7 ] ) ){

    print( paste( "Usage: Rscript SCPFbatchFlowResp",
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

postOutputFile <- paste( args[ 7 ],
                         args[ 5 ],
                         "_",
                         args[ 6 ],
                         "_PostGraph.jpg",
                         sep="" )

delOutputFile <- paste( args[ 7 ],
                        args[ 5 ],
                        "_",
                        args[ 6 ],
                        "_DelGraph.jpg",
                        sep="" )

postChartTitle <- paste( "Single Bench Flow Latency - Post", "Last 3 Builds", sep = "\n" )
delChartTitle <- paste( "Single Bench Flow Latency - Del", "Last 3 Builds", sep = "\n" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- dbConnect( dbDriver( "PostgreSQL" ),
                  dbname = "onostest",
                  host = args[ 1 ],
                  port = strtoi( args[ 2 ] ),
                  user = args[ 3 ],
                  password = args[ 4 ] )

# ---------------------------
# Batch Flow Resp SQL Command
# ---------------------------

print( "Generating Batch Flow Resp SQL Command" )

command <- paste( "SELECT * FROM batch_flow_tests WHERE branch='",
                  args[ 6 ],
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

# -----------------
# Post Data Sorting
# -----------------

print( "Sorting data for Post." )

postAvgs <- c( fileData[ 'posttoconfrm' ],
               fileData[ 'elapsepost' ] )

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

print( "Sorting data for Del." )
avgs <- c( fileData[ 'deltoconfrm' ],
           fileData[ 'elapsedel' ] )

# ------------------------
# Del Construct Data Frame
# ------------------------

delDataFrame <- melt( avgs )
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
yLabel <- ylab( "Latency (ms)" )
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
                legend.key.size = unit( 1.5, 'lines' ) )

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
title <- ggtitle( postChartTitle )


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

ggsave( postOutputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

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
title <- ggtitle( delChartTitle )

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

ggsave( delOutputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote stacked bar chart out to", delOutputFile ) )