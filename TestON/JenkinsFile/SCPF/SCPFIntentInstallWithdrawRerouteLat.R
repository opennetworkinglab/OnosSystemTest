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
if ( is.na( args[ 9 ] ) ){
    print( "Usage: Rscript SCPFIntentInstallWithdrawRerouteLat.R <isFlowObj> <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <batch-size> <directory-to-save-graphs>" )
    q()  # basically exit(), but in R
}

flowObjFileModifier <- ""
if ( args[ 1 ] == "y" ){
    flowObjFileModifier <- "fobj_"
}

# Filenames for output graphs include the testname and the graph type.
# See the examples below. paste() is used to concatenate strings.

errBarOutputFile <- paste( args[ 9 ], "SCPFIntentInstallWithdrawRerouteLat", sep="" )
errBarOutputFile <- paste( errBarOutputFile, args[ 7 ], sep="_" )
if ( args[ 1 ] == "y" ){
    errBarOutputFile <- paste( errBarOutputFile, "_fobj", sep="" )
}
errBarOutputFile <- paste( errBarOutputFile, "_", sep="" )
errBarOutputFile <- paste( errBarOutputFile, args[ 8 ], sep="" )
errBarOutputFile <- paste( errBarOutputFile, "-batchSize", sep="" )
errBarOutputFile <- paste( errBarOutputFile, "_graph.jpg", sep="" )

print( "Reading from databases." )

con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 2 ], port=strtoi( args[ 3 ] ), user=args[ 4 ],password=args[ 5 ] )

command1 <- paste( "SELECT * FROM intent_latency_", flowObjFileModifier, sep="" )
command1 <- paste( command1, "tests WHERE batch_size=", sep="" )
command1 <- paste( command1, args[ 8 ], sep="" )
command1 <- paste( command1, " AND branch = '", sep="" )
command1 <- paste( command1, args[ 7 ], sep="" )
command1 <- paste( command1, "' AND date IN ( SELECT MAX( date ) FROM intent_latency_", sep="" )
command1 <- paste( command1, flowObjFileModifier, sep="" )
command1 <- paste( command1,  "tests WHERE branch='", sep="" )
command1 <- paste( command1,  args[ 7 ], sep="" )
command1 <- paste( command1,  "')", sep="" )

print( paste( "Sending SQL command:", command1 ) )

fileData1 <- dbGetQuery( con, command1 )

command2 <- paste( "SELECT * FROM intent_reroute_latency_", flowObjFileModifier, sep="" )
command2 <- paste( command2, "tests WHERE batch_size=", sep="" )
command2 <- paste( command2, args[ 8 ], sep="" )
command2 <- paste( command2, " AND branch = '", sep="" )
command2 <- paste( command2, args[ 7 ], sep="" )
command2 <- paste( command2, "' AND date IN ( SELECT MAX( date ) FROM intent_reroute_latency_", sep="" )
command2 <- paste( command2, flowObjFileModifier, sep="" )
command2 <- paste( command2,  "tests WHERE branch='", sep="" )
command2 <- paste( command2,  args[ 7 ], sep="" )
command2 <- paste( command2,  "')", sep="" )

print( paste( "Sending SQL command:", command2 ) )

fileData2 <- dbGetQuery( con, command2 )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "STEP 2: Organize data." )

# Create lists c() and organize data into their corresponding list.
print( "Sorting data." )
if ( ncol( fileData2 ) == 0 ){
    avgs <- c( fileData1[ 'install_avg' ], fileData1[ 'withdraw_avg' ] )
} else{
    colnames( fileData2 ) <- c( "date", "name", "date", "branch", "commit", "scale", "batch_size", "reroute_avg", "reroute_std" )
    avgs <- c( fileData1[ 'install_avg' ], fileData1[ 'withdraw_avg' ], fileData2[ 'reroute_avg' ] )
}

# Parse lists into data frames.
dataFrame <- melt( avgs )              # This is where reshape2 comes in. Avgs list is converted to data frame

if ( ncol( fileData2 ) == 0 ){
    dataFrame$scale <- c( fileData1$scale, fileData1$scale )      # Add node scaling to the data frame.
    dataFrame$stds <- c( fileData1$install_std, fileData1$withdraw_std )
} else{
    dataFrame$scale <- c( fileData1$scale, fileData1$scale, fileData2$scale )      # Add node scaling to the data frame.
    dataFrame$stds <- c( fileData1$install_std, fileData1$withdraw_std, fileData2$reroute_std )
}
colnames( dataFrame ) <- c( "ms", "type", "scale", "stds" )

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$type <- as.character( dataFrame$type )
dataFrame$type <- factor( dataFrame$type, levels=unique( dataFrame$type ) )

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
if ( min( dataFrame$ms - dataFrame$stds ) < 0){
    yWindowMin <- min( dataFrame$ms - dataFrame$stds ) * 1.05
} else {
    yWindowMin <- 0
}
yWindowMax <- max( dataFrame$ms + dataFrame$stds )

mainPlot <- ggplot( data = dataFrame, aes( x = scale, y = ms, ymin = ms - stds, ymax = ms + stds,fill = type ) )

# Formatting the plot
width <- 1.3  # Width of the bars.
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9) )
yLimit <- ylim( yWindowMin, yWindowMax )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
chartTitle <- "Intent Install, Withdraw, & Reroute Latencies"
if ( args[ 1 ] == "y" ){
    chartTitle <- paste( chartTitle, "with Flow Objectives" )
}
chartTitle <- paste( chartTitle, "\nBatch Size =" )
chartTitle <- paste( chartTitle, fileData1[ 1,'batch_size' ] )

theme <- theme( plot.title=element_text( hjust = 0.5, size = 18, face='bold' ) )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot + xScaleConfig + yLimit + xLabel + yLabel + fillLabel + theme


# Create the bar graph with error bars.
# geom_bar contains:
#    - stat: data formatting (usually "identity")
#    - width: the width of the bar types (declared above)
# geom_errorbar contains similar arguments as geom_bar.
print( "Generating bar graph with error bars." )
barGraphFormat <- geom_bar( stat = "identity", width = width, position = "dodge" )
errorBarFormat <- geom_errorbar( width = width, position = "dodge" )
title <- ggtitle( chartTitle )
result <- fundamentalGraphData + barGraphFormat + errorBarFormat + title

# Save graph to file
print( paste( "Saving bar chart with error bars to", errBarOutputFile ) )
ggsave( errBarOutputFile, width = 10, height = 6, dpi = 200 )
print( paste( "Successfully wrote bar chart with error bars out to", errBarOutputFile ) )
