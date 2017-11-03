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
has_flow_obj = 1
database_host = 2
database_port = 3
database_u_id = 4
database_pw = 5
test_name = 6
branch_name = 7
has_neighbors = 8
old_flow = 9
save_directory = 10

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

    print( paste( "Usage: Rscript SCPFIntentEventTp.R",
                                  "<has-flow-obj>",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<has-neighbors>",
                                  "<using-old-flow>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    q()  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

chartTitle <- "Intent Event Throughput"
fileNeighborsModifier <- "no"
commandNeighborModifier <- ""
fileFlowObjModifier <- ""
sqlFlowObjModifier <- ""

if ( args[ has_flow_obj ] == 'y' ){
    fileFlowObjModifier <- "_flowObj"
    sqlFlowObjModifier <- "_fobj"
    chartTitle <- paste( chartTitle, " with Flow Objectives", sep="" )
}

chartTitle <- paste( chartTitle, "\nevents/second with Neighbors =", sep="" )

fileOldFlowModifier <- ""
if ( args[ has_neighbors ] == 'y' ){
    fileNeighborsModifier <- "all"
    commandNeighborModifier <- "scale=1 OR NOT "
    chartTitle <- paste( chartTitle, "all" )
} else {
    chartTitle <- paste( chartTitle, "0" )
}
if ( args[ old_flow ] == 'y' ){
    fileOldFlowModifier <- "_OldFlow"
    chartTitle <- paste( chartTitle, "With Old Flow", sep="\n" )
}

errBarOutputFile <- paste( args[ save_directory ],
                           args[ test_name ],
                           "_",
                           args[ branch_name ],
                           "_",
                           fileNeighborsModifier,
                           "-neighbors",
                           fileFlowObjModifier,
                           fileOldFlowModifier,
                           "_graph.jpg",
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

# -----------------------------------
# Intent Event Throughput SQL Command
# -----------------------------------

print( "Generating Intent Event Throughput SQL command." )

command <- paste( "SELECT scale, SUM( avg ) as avg FROM intent_tp",
                  sqlFlowObjModifier,
                  "_tests WHERE (",
                  commandNeighborModifier,
                  "neighbors = 0 ) AND branch = '",
                  args[ branch_name ],
                  "' AND date IN ( SELECT max( date ) FROM intent_tp",
                  sqlFlowObjModifier,
                  "_tests WHERE branch='",
                  args[ branch_name ],
                  "' AND ",
                  ( if( args[ old_flow ] == 'y' ) "" else "NOT " ),
                  "is_old_flow",
                  " ) GROUP BY scale ORDER BY scale",
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
avgs <- c( fileData[ 'avg' ] )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing data frame." )
dataFrame <- melt( avgs )              # This is where reshape2 comes in. Avgs list is converted to data frame
dataFrame$scale <- fileData$scale          # Add node scaling to the data frame.

colnames( dataFrame ) <- c( "throughput",
                            "type",
                            "scale" )

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

print( "Generating main plot." )
# Create the primary plot here.
# ggplot contains the following arguments:
#     - data: the data frame that the graph will be based off of
#    - aes: the asthetics of the graph which require:
#        - x: x-axis values (usually node scaling)
#        - y: y-axis values (usually time in milliseconds)
#        - fill: the category of the colored side-by-side bars (usually type)

mainPlot <- ggplot( data = dataFrame, aes( x = scale,
                                           y = throughput,
                                           fill = type ) )
# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

# Formatting the plot
theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
width <- 0.7  # Width of the bars.
xScaleConfig <- scale_x_continuous( breaks = dataFrame$scale, label = dataFrame$scale )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Throughput (events/second)" )
fillLabel <- labs( fill="Type" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size = 18, face = "bold" ),
                legend.title = element_blank() )

values <- geom_text( aes( x = dataFrame$scale,
                          y = dataFrame$throughput + 0.03 * max( dataFrame$throughput ),
                          label = format( dataFrame$throughput,
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7,
                          fontface = "bold" )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        values

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph." )
barGraphFormat <- geom_bar( stat = "identity",
                            width = width,
                            fill = "#169EFF" )

title <- ggtitle( chartTitle )

result <- fundamentalGraphData +
          barGraphFormat +
          title

# -----------------------
# Exporting Graph to File
# -----------------------

print( paste( "Saving bar chart to", errBarOutputFile ) )

ggsave( errBarOutputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote bar chart out to", errBarOutputFile ) )
