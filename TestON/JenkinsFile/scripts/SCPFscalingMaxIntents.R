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
old_flow = 8
save_directory = 9

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
    print( paste( "Usage: Rscript SCPFInstalledIntentsFlows",
                                  "<has-flowObj>",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<using-old-flow>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    quit( status = 1 )  # basically exit(), but in R
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

fileFlowObjModifier <- ""
sqlFlowObjModifier <- ""
chartTitle <- "Number of Installed Intents & Flows"

if ( args[ has_flow_obj ] == "y" ){
    fileFlowObjModifier <- "_flowObj"
    sqlFlowObjModifier <- "fobj_"
    chartTitle <- "Number of Installed Intents & Flows\n with Flow Objectives"
}
fileOldFlowModifier <- ""
if ( args[ old_flow ] == 'y' ){
    fileOldFlowModifier <- "_OldFlow"
    chartTitle <- paste( chartTitle, "With Eventually Consistent Flow Rule Store", sep="\n" )
}

outputFile <- paste( args[ save_directory ],
                     args[ test_name ],
                     fileFlowObjModifier,
                     fileOldFlowModifier,
                     "_",
                     args[ branch_name ],
                     "_errGraph.jpg",
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

# -------------------------------
# Scaling Max Intents SQL Command
# -------------------------------

print( "Scaling Max Intents SQL Command" )

command <- paste( "SELECT * FROM max_intents_",
                  sqlFlowObjModifier,
                  "tests WHERE branch = '",
                  args[ branch_name ],
                  "' AND date IN ( SELECT MAX( date ) FROM max_intents_",
                  sqlFlowObjModifier,
                  "tests WHERE branch = '",
                  args[ branch_name ],
                  "' AND ",
                  ( if( args[ old_flow ] == 'y' ) "" else "NOT " ),
                  "is_old_flow",
                  " ) ",
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

requiredColumns <- c( "max_intents_ovs", "max_flows_ovs" )

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
dataFrame$scale <- fileData$scale

colnames( dataFrame ) <- c( "ms", "type", "scale" )

dataFrame$type <- as.character( dataFrame$type )
dataFrame$type <- factor( dataFrame$type, levels=unique( dataFrame$type ) )

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
mainPlot <- ggplot( data = dataFrame, aes( x = scale,
                                           y = ms,
                                           fill = type ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

barWidth <- 1.3
theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9 ) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Max Number of Intents/Flow Rules" )
fillLabel <- labs( fill="Type" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face = 'bold' ),
                legend.position = "bottom",
                legend.text = element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

colors <- scale_fill_manual( values = c( "#F77670",
                                         "#619DFA" ) )

wrapLegend <- guides( fill = guide_legend( nrow = 1, byrow = TRUE ) )
title <- ggtitle( chartTitle )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        wrapLegend +
                        title +
                        colors

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph." )

barGraphFormat <- geom_bar( stat = "identity",
                            position = position_dodge(),
                            width = barWidth )

values <- geom_text( aes( x = dataFrame$scale,
                          y = dataFrame$ms + 0.015 * max( dataFrame$ms ),
                          label = format( dataFrame$ms,
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 5.2,
                          fontface = "bold",
                          position = position_dodge( width = 1.25 ) )

result <- fundamentalGraphData +
          barGraphFormat +
          values

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
