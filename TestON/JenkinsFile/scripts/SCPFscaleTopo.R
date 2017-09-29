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
# please contact Jeremy Ronquillo: jeremyr@opennetworking.org

# **********************************************************
# STEP 1: File management.
# **********************************************************

print( "STEP 1: File management." )

# Command line arguments are read. Args usually include the database filename and the output
# directory for the graphs to save to.
# ie: Rscript SCPFgraphGenerator SCPFsampleDataDB.csv ~/tmp/
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# Import libraries to be used for graphing and organizing data, respectively.
# Find out more about ggplot2: https://github.com/tidyverse/ggplot2
#                     reshape2: https://github.com/hadley/reshape
print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )    # For databases

# Check if sufficient args are provided.
if ( is.na( args[ 7 ] ) ){
    print( "Usage: Rscript SCPFgraphGenerator <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <directory-to-save-graphs>" )
    q()  # basically exit(), but in R
}

# Filenames for output graphs include the testname and the graph type.
# See the examples below. paste() is used to concatenate strings.

outputFile <- paste( args[ 7 ], args[ 5 ], sep="" )
outputFile <- paste( outputFile, args[ 6 ], sep="_" )
outputFile <- paste( outputFile, "_graph.jpg", sep="" )

print( "Reading from databases." )

con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 1 ], port=strtoi( args[ 2 ] ), user=args[ 3 ],password=args[ 4 ] )

command  <- paste( "SELECT * FROM scale_topo_latency_details WHERE branch = '", args[ 6 ], sep = "" )
command <- paste( command, "' AND date IN ( SELECT MAX( date ) FROM scale_topo_latency_details WHERE branch = '", sep = "" )
command <- paste( command, args[ 6 ], sep = "" )
command <- paste( command, "' ) ", sep="" )

print( paste( "Sending SQL command:", command ) )

fileData <- dbGetQuery( con, command )

title <- paste( args[ 5 ], args[ 6 ], sep="_" )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "STEP 2: Organize data." )

# Create lists c() and organize data into their corresponding list.
print( "Sorting data." )
avgs <- c( fileData[ 'last_role_request_to_last_topology' ], fileData[ 'last_connection_to_last_role_request' ], fileData[ 'first_connection_to_last_connection' ] )

# Parse lists into data frames.
dataFrame <- melt( avgs )              # This is where reshape2 comes in. Avgs list is converted to data frame
dataFrame$scale <- fileData$scale          # Add node scaling to the data frame.
colnames( dataFrame ) <- c( "ms", "type", "scale")


# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$type <- as.character( dataFrame$type )
dataFrame$type <- factor( dataFrame$type, levels=unique( dataFrame$type ) )
dataFrame$iterative <- seq( 1, nrow( fileData ), by = 1 )

# Obtain the sum of the averages for the plot size and center of standard deviation bars.
avgsSum <- fileData$total_time

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "STEP 3: Generate graphs." )

# 1. Graph fundamental data is generated first.
#    These are variables that apply to all of the graphs being generated, regardless of type.
#
# 2. Type specific graph data is generated.
#     Data specific for the error bar and stacked bar graphs are generated.
#
# 3. Generate and save the graphs.
#      Graphs are saved to the filename above, in the directory provided in command line args

print( "Generating fundamental graph data." )

# Calculate window to display graph, based on the lowest and highest points of the data.
if ( min( avgsSum ) < 0){
    yWindowMin <- min( avgsSum ) * 1.05
} else {
    yWindowMin <- 0
}
yWindowMax <- max( avgsSum ) * 1.2

theme_set( theme_grey( base_size = 20 ) )   # set the default text size of the graph.

# Create the primary plot here.
# ggplot contains the following arguments:
#     - data: the data frame that the graph will be based off of
#    - aes: the asthetics of the graph which require:
#        - x: x-axis values (usually node scaling)
#        - y: y-axis values (usually time in milliseconds)
#        - fill: the category of the colored side-by-side bars (usually type)
mainPlot <- ggplot( data = dataFrame, aes( x = iterative, y = ms, fill = type ) )

# Formatting the plot
width <- 0.6  # Width of the bars.
xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative, label = dataFrame$scale )
yLimit <- ylim( yWindowMin, yWindowMax )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
chartTitle <- paste( "Scale Topology Latency Test" )
theme <- theme( plot.title=element_text( hjust = 0.5, size = 28, face='bold' ) )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot + xScaleConfig + yLimit + xLabel + yLabel + fillLabel + theme

# Create the stacked bar graph with error bars.
# geom_bar contains:
#    - stat: data formatting (usually "identity")
#    - width: the width of the bar types (declared above)
# geom_errorbar contains similar arguments as geom_bar.
print( "Generating bar graph with error bars." )
barGraphFormat <- geom_bar( stat = "identity", width = width )
title <- ggtitle( paste( chartTitle, "" ) )
result <- fundamentalGraphData + barGraphFormat + title

# Save graph to file
print( paste( "Saving bar chart with error bars to", outputFile ) )
ggsave( outputFile, width = 10, height = 6, dpi = 200 )
print( paste( "Successfully wrote bar chart with error bars out to", outputFile ) )
