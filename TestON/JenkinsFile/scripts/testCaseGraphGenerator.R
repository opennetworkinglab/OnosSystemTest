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

# This is the R script that generates the FUNC, HA, and various USECASE result graphs.

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( is.na( args[ 8 ] ) ){

    print( paste( "Usage: Rscript testCaseGraphGenerator.R",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",                      # part of the output filename
                                  "<branch-name>",                    # for sql and output filename
                                  "<#-builds-to-show>",               # for sql and output filename
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    q()  # basically exit(), but in R
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

title <- paste( args[ 5 ],
                " - ",
                args[ 6 ],
                " \n Results of Last ",
                args[ 7 ],
                " Builds",
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ 8 ],
                     args[ 5 ],
                     "_",
                     args[ 6 ],
                     "_",
                     args[ 7 ],
                     "-builds_graph.jpg",
                     sep="" )

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

# ---------------------
# Test Case SQL Command
# ---------------------
print( "Generating Test Case SQL command." )

command <- paste( "SELECT * FROM executed_test_tests WHERE actual_test_name='",
                  args[ 5 ],
                  "' AND branch='",
                  args[ 6 ],
                  "' ORDER BY date DESC LIMIT ",
                  args[ 7 ],
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

# -------------------------------------------------------
# Combining Passed, Failed, and Planned Data
# -------------------------------------------------------

print( "Combining Passed, Failed, and Planned Data." )

categories <- c( fileData[ 'num_failed' ],
                 fileData[ 'num_passed' ],
                 fileData[ 'num_planned' ] )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing data frame from combined data." )

dataFrame <- melt( categories )

# Rename column names in dataFrame
colnames( dataFrame ) <- c( "Tests",
                            "Status" )

# Add build dates to the dataFrame
dataFrame$build <- fileData$build

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$Status <- as.character( dataFrame$Status )
dataFrame$Status <- factor( dataFrame$Status, levels = unique( dataFrame$Status ) )

# Add planned, passed, and failed results to the dataFrame (for the fill below the lines)
dataFrame$num_planned <- fileData$num_planned
dataFrame$num_passed <- fileData$num_passed
dataFrame$num_failed <- fileData$num_failed

# Adding a temporary reversed iterative list to the dataFrame so that there are no gaps in-between build numbers.
dataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

# Omit any data that doesn't exist
dataFrame <- na.omit( dataFrame )

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# -------------------
# Main Plot Generated
# -------------------

print( "Creating main plot." )
# Create the primary plot here.
# ggplot contains the following arguments:
#     - data: the data frame that the graph will be based off of
#    - aes: the asthetics of the graph which require:
#        - x: x-axis values (usually iterative, but it will become build # later)
#        - y: y-axis values (usually tests)
#        - color: the category of the colored lines (usually status of test)

mainPlot <- ggplot( data = dataFrame, aes( x = iterative,
                                           y = Tests,
                                           color = Status ) )

# -------------------
# Main Plot Formatted
# -------------------

print( "Formatting main plot." )

# geom_ribbon is used so that there is a colored fill below the lines. These values shouldn't be changed.
failedColor <- geom_ribbon( aes( ymin = 0,
                                 ymax = dataFrame$num_failed ),
                                 fill = "red",
                                 linetype = 0,
                                 alpha = 0.07 )

passedColor <- geom_ribbon( aes( ymin = 0,
                                 ymax = dataFrame$num_passed ),
                                 fill = "green",
                                 linetype = 0,
                                 alpha = 0.05 )

plannedColor <- geom_ribbon( aes( ymin = 0,
                                  ymax = dataFrame$num_planned ),
                                  fill = "blue",
                                  linetype = 0,
                                  alpha = 0.01 )

# Colors for the lines
lineColors <- scale_color_manual( values=c( "#E80000",      # red
                                            "#00B208",      # green
                                            "#00A5FF") )    # blue

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$build )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$Tests ),
                                    by = ceiling( max( dataFrame$Tests ) / 10 ) ) )

xLabel <- xlab( "Build Number" )
yLabel <- ylab( "Test Cases" )

imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

legendLabels <- scale_colour_discrete( labels = c( "Failed Cases",
                                                   "Passed Cases",
                                                   "Planned Cases" ) )

# Set other graph configurations here.
theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face ='bold' ),
                axis.text.x = element_text( angle = 0, size = 14 ),
                legend.position = "bottom",
                legend.text = element_text( size = 22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ) )

title <- ggtitle( title )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        plannedColor +
                        passedColor +
                        failedColor +
                        xScaleConfig +
                        yScaleConfig +
                        xLabel +
                        yLabel +
                        lineColors +
                        legendLabels +
                        theme +
                        title

# ----------------------------
# Generating Line Graph Format
# ----------------------------

print( "Generating line graph." )

lineGraphFormat <- geom_line( size = 1.1 )
pointFormat <- geom_point( size = 3 )

result <- fundamentalGraphData +
           lineGraphFormat +
           pointFormat

# -----------------------
# Exporting Graph to File
# -----------------------

print( paste( "Saving result graph to", outputFile ) )

ggsave( outputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote result graph out to", outputFile ) )
