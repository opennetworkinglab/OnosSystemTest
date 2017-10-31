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

print( "STEP 1: Data management." )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# Import libraries to be used for graphing and organizing data, respectively.
# Find out more about ggplot2: https://github.com/tidyverse/ggplot2
#                     reshape2: https://github.com/hadley/reshape
#                      RPostgreSQL: https://code.google.com/archive/p/rpostgresql/
print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )

# Check if sufficient args are provided.
if ( is.na( args[ 8 ] ) ){
    print( "Usage: Rscript testCaseGraphGenerator.R <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <#-builds-to-show> <directory-to-save-graphs>" )
    q()  # basically exit(), but in R
}

# Filenames for the output graph include the testname, branch, and the graph type.
outputFile <- paste( args[ 8 ], args[ 5 ], sep="" )
outputFile <- paste( outputFile, args[ 6 ], sep="_" )
outputFile <- paste( outputFile, args[ 7 ], sep="_" )
outputFile <- paste( outputFile, "builds", sep="-" )
outputFile <- paste( outputFile, "_graph.jpg", sep="" )

# From RPostgreSQL
print( "Reading from databases." )
con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 1 ], port=strtoi( args[ 2 ] ), user=args[ 3 ],password=args[ 4 ] )

print( "Creating SQL command." )
# Creating SQL command based on command line args.
command <- paste( "SELECT * FROM executed_test_tests WHERE actual_test_name='", args[ 5 ], sep="" )
command <- paste( command, "' AND branch='", sep="" )
command <- paste( command, args[ 6 ], sep="" )
command <- paste( command, "' ORDER BY date DESC LIMIT ", sep="" )
command <- paste( command, args[ 7 ], sep="" )
fileData <- dbGetQuery( con, command )

# Title of graph based on command line args.
title <- paste( args[ 5 ], args[ 6 ], sep=" - " )
title <- paste( title, "Results of Last ", sep=" \n " )
title <- paste( title, args[ 7 ], sep="" )
title <- paste( title, " Builds", sep="" )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "STEP 2: Organize data." )

# Create lists c() and organize data into their corresponding list.
print( "Sorting data into new data frame." )
categories <- c( fileData[ 'num_failed' ], fileData[ 'num_passed' ], fileData[ 'num_planned' ] )

# Parse lists into data frames.
# This is where reshape2 comes in. Avgs list is converted to data frame.
dataFrame <- melt( categories )
dataFrame$build <- fileData$build
colnames( dataFrame ) <- c( "Tests", "Status", "Build" )

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$Status <- as.character( dataFrame$Status )
dataFrame$Status <- factor( dataFrame$Status, levels=unique( dataFrame$Status ) )

# Add planned, passed, and failed results to the dataFrame (for the fill below the lines)
dataFrame$num_planned <- fileData$num_planned
dataFrame$num_passed <- fileData$num_passed
dataFrame$num_failed <- fileData$num_failed

# Adding a temporary reversed iterative list to the dataFrame so that there are no gaps in-between build numbers.
dataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "STEP 3: Generate graphs." )

print( "Creating main plot." )
# Create the primary plot here.
# ggplot contains the following arguments:
#     - data: the data frame that the graph will be based off of
#    - aes: the asthetics of the graph which require:
#        - x: x-axis values (usually iterative, but it will become build # later)
#        - y: y-axis values (usually tests)
#        - color: the category of the colored lines (usually status of test)
theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.
mainPlot <- ggplot( data = dataFrame, aes( x = iterative, y = Tests, color = Status ) )

print( "Formatting main plot." )
# geom_ribbon is used so that there is a colored fill below the lines. These values shouldn't be changed.
failedColor <- geom_ribbon( aes( ymin = 0, ymax = dataFrame$num_failed ), fill = "red", linetype = 0, alpha = 0.07 )
passedColor <- geom_ribbon( aes( ymin = 0, ymax = dataFrame$num_passed ), fill = "green", linetype = 0, alpha = 0.05 )
plannedColor <- geom_ribbon( aes( ymin = 0, ymax = dataFrame$num_planned ), fill = "blue", linetype = 0, alpha = 0.01 )

colors <- scale_color_manual( values=c( "#E80000", "#00B208", "#00A5FF") )

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative, label = dataFrame$Build )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$Tests ), by = ceiling( max( dataFrame$Tests ) / 10 ) ) )

xLabel <- xlab( "Build Number" )
yLabel <- ylab( "Test Cases" )
fillLabel <- labs( fill="Type" )
legendLabels <- scale_colour_discrete( labels = c( "Failed Cases", "Passed Cases", "Planned Cases" ) )
centerTitle <- theme( plot.title=element_text( hjust = 0.5 ) )  # To center the title text
theme <- theme( plot.title = element_text( size = 32, face='bold' ), axis.text.x = element_text( angle = 0, size = 14 ), legend.position="bottom", legend.text=element_text( size=22 ), legend.title = element_blank(), legend.key.size = unit( 1.5, 'lines' ) )


# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot + plannedColor + passedColor + failedColor + xScaleConfig + yScaleConfig + xLabel + yLabel + fillLabel + colors + legendLabels + centerTitle + theme

print( "Generating line graph." )

lineGraphFormat <- geom_line( size = 1.1 )
pointFormat <- geom_point( size = 3 )
title <- ggtitle( title )

result <- fundamentalGraphData + lineGraphFormat + pointFormat + title

# Save graph to file
print( paste( "Saving result graph to", outputFile ) )
ggsave( outputFile, width = 15, height = 10, dpi = 200 )
print( paste( "Successfully wrote result graph out to", outputFile ) )
