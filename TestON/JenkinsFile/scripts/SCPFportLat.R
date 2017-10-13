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
# STEP 1: File management.
# **********************************************************

print( "STEP 1: File management." )

# Command line arguments are read.
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
    print( "Usage: Rscript SCPFportLat <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <directory-to-save-graphs>" )
    q()  # basically exit(), but in R
}

# paste() is used to concatenate strings.
errBarOutputFileUp <- paste( args[ 7 ], "SCPFportLat_", sep = "" )
errBarOutputFileUp <- paste( errBarOutputFileUp, args[ 6 ], sep = "" )
errBarOutputFileUp <- paste( errBarOutputFileUp, "_UpErrBarWithStack.jpg", sep = "" )

errBarOutputFileDown <- paste( args[ 7 ], "SCPFportLat_", sep = "" )
errBarOutputFileDown <- paste( errBarOutputFileDown, args[ 6 ], sep = "" )
errBarOutputFileDown <- paste( errBarOutputFileDown, "_DownErrBarWithStack.jpg", sep = "" )

print( "Reading from databases." )

con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 1 ], port=strtoi( args[ 2 ] ), user=args[ 3 ],password=args[ 4 ] )

command  <- paste( "SELECT * FROM port_latency_details WHERE branch = '", args[ 6 ], sep = "" )
command <- paste( command, "' AND date IN ( SELECT MAX( date ) FROM port_latency_details WHERE branch = '", sep = "" )
command <- paste( command, args[ 6 ], sep = "" )
command <- paste( command, "' ) ", sep="" )

print( paste( "Sending SQL command:", command ) )

fileData <- dbGetQuery( con, command )

chartTitle <- paste( "Port Latency", args[ 6 ], sep = " - " )
chartTitle <- paste( chartTitle, "\n" )


# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "Sorting data." )

upAvgs <- c( fileData[ 'up_ofp_to_dev_avg' ], fileData[ 'up_dev_to_link_avg' ], fileData[ 'up_link_to_graph_avg' ] )
upAvgsData <- melt( upAvgs )
upAvgsData$scale <- fileData$scale
upAvgsData$up_std <- fileData$up_std


colnames( upAvgsData ) <- c( "ms", "type", "scale", "stds" )
upAvgsData$type <- as.character( upAvgsData$type )
upAvgsData$type <- factor( upAvgsData$type, levels=unique( upAvgsData$type ) )

downAvgs <- c( fileData[ 'down_ofp_to_dev_avg' ], fileData[ 'down_dev_to_link_avg' ], fileData[ 'down_link_to_graph_avg' ] )
downAvgsData <- melt( downAvgs )
downAvgsData$scale <- fileData$scale
downAvgsData$down_std <- fileData$down_std

colnames( downAvgsData ) <- c( "ms", "type", "scale", "stds" )
downAvgsData$type <- as.character( downAvgsData$type )
downAvgsData$type <- factor( downAvgsData$type, levels=unique( downAvgsData$type ) )

upAvgsData <- na.omit( upAvgsData )   # Omit any data that doesn't exist
downAvgsData <- na.omit( downAvgsData )   # Omit any data that doesn't exist

print( "Up Averages Results:" )
print( upAvgsData )

print( "Down Averages Results:" )
print( downAvgsData )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************


print( "Generating fundamental graph data (Port Up Latency)." )
width <- 1
theme_set( theme_grey( base_size = 20 ) )   # set the default text size of the graph.

mainPlot <- ggplot( data = upAvgsData, aes( x = scale, y = ms, fill = type, ymin = fileData[ 'up_end_to_end_avg' ] - stds, ymax = fileData[ 'up_end_to_end_avg' ] + stds ) )
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
theme <- theme( plot.title=element_text( hjust = 0.5, size = 28, face='bold' ) )

fundamentalGraphData <- mainPlot + xScaleConfig + xLabel + yLabel + fillLabel + theme

print( "Generating bar graph with error bars (Port Up Latency)." )
barGraphFormat <- geom_bar( stat="identity", width = width )
errorBarFormat <- geom_errorbar( width = width, color=rgb( 140, 140, 140, maxColorValue=255 ) )
sum <- fileData[ 'up_ofp_to_dev_avg' ] + fileData[ 'up_dev_to_link_avg' ] + fileData[ 'up_link_to_graph_avg' ]
values <- geom_text( aes( x=upAvgsData$scale, y=sum + 0.04 * max( sum ), label = format( sum, digits=3, big.mark = ",", scientific = FALSE ) ), size = 5, fontface = "bold" )
title <- ggtitle( "Port Up Latency" )
result <- fundamentalGraphData + barGraphFormat + errorBarFormat + title + values


print( paste( "Saving bar chart with error bars (Port Up Latency) to", errBarOutputFileUp ) )
ggsave( errBarOutputFileUp, width = 10, height = 6, dpi = 200 )


print( paste( "Successfully wrote bar chart with error bars (Port Up Latency) out to", errBarOutputFileUp ) )


print( "Generating fundamental graph data (Port Down Latency)." )

mainPlot <- ggplot( data = downAvgsData, aes( x = scale, y = ms, fill = type, ymin = fileData[ 'down_end_to_end_avg' ] - stds, ymax = fileData[ 'down_end_to_end_avg' ] + stds ) )
theme <- theme( plot.title=element_text( hjust = 0.5, size = 28, face='bold' ) )

fundamentalGraphData <- mainPlot + xScaleConfig + xLabel + yLabel + fillLabel + theme

print( "Generating bar graph with error bars (Port Down Latency)." )
barGraphFormat <- geom_bar( stat="identity", width = width )
errorBarFormat <- geom_errorbar( width = width, color=rgb( 140, 140, 140, maxColorValue=255 ) )
sum <- fileData[ 'down_ofp_to_dev_avg' ] + fileData[ 'down_dev_to_link_avg' ] + fileData[ 'down_link_to_graph_avg' ]
values <- geom_text( aes( x=downAvgsData$scale, y=sum + 0.04 * max( sum ), label = format( sum, digits=3, big.mark = ",", scientific = FALSE ) ), size = 5, fontface = "bold" )

title <- ggtitle( "Port Down Latency" )
result <- fundamentalGraphData + barGraphFormat + errorBarFormat + title + values


print( paste( "Saving bar chart with error bars (Port Down Latency) to", errBarOutputFileDown ) )
ggsave( errBarOutputFileDown, width = 10, height = 6, dpi = 200 )


print( paste( "Successfully wrote bar chart with error bars (Port Down Latency) out to", errBarOutputFileDown ) )
