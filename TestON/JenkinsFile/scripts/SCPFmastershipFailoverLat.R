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

# Normal usage
# Check if sufficient args are provided.
if ( is.na( args[ 7 ] ) ){
    print( "Usage: Rscript SCPFmastershipFailoverLat <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <directory-to-save-graphs>" )
        q()  # basically exit(), but in R
}

# Filenames for output graphs include the testname and the graph type.
# See the examples below. paste() is used to concatenate strings.

errBarOutputFile <- paste( args[ 7 ], args[ 5 ], sep="" )
errBarOutputFile <- paste( errBarOutputFile, args[ 6 ], sep="_" )
errBarOutputFile <- paste( errBarOutputFile, "_errGraph.jpg", sep="" )

stackedBarOutputFile <- paste( args[ 7 ], args[ 5 ], sep="" )
stackedBarOutputFile <- paste( stackedBarOutputFile, args[ 6 ], sep="_" )
stackedBarOutputFile <- paste( stackedBarOutputFile, "_stackedGraph.jpg", sep="" )

print( "Reading from databases." )

con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 1 ], port=strtoi( args[ 2 ] ), user=args[ 3 ],password=args[ 4 ] )

command  <- paste( "SELECT * FROM mastership_failover_tests WHERE branch = '", args[ 6 ], sep = "" )
command <- paste( command, "' AND date IN ( SELECT MAX( date ) FROM mastership_failover_tests WHERE branch = '", sep = "" )
command <- paste( command, args[ 6 ], sep = "" )
command <- paste( command, "' ) ", sep="" )

print( paste( "Sending SQL command:", command ) )

fileData <- dbGetQuery( con, command )

chartTitle <- "Mastership Failover Latency"


# **********************************************************
# STEP 2: Organize data.
# **********************************************************

fileDataNames <- names( fileData )

avgs <- c()
stds <- c()


print( "Sorting data." )
for ( name in fileDataNames ){
    nameLen <- nchar( name )
    if ( nameLen > 2 ){
        if ( substring( name, nameLen - 2, nameLen ) == "avg" ){
            avgs <- c( avgs, fileData[ name ] )
        }
        if ( substring( name, nameLen - 2, nameLen ) == "std" ){
            stds <- c( stds, fileData[ name  ] )
        }
    }
}

avgData <- melt( avgs )
avgData$scale <- fileData$scale
colnames( avgData ) <- c( "ms", "type", "scale" )

stdData <- melt( stds )
colnames( stdData ) <- c( "ms", "type" )

dataFrame <- na.omit( avgData )   # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( avgData )


# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 20 ) )   # set the default text size of the graph.

mainPlot <- ggplot( data = avgData, aes( x = scale, y = ms, ymin = ms - stdData$ms, ymax = ms + stdData$ms,fill = type ) )
xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9) )
yLimit <- ylim( yMin, yMax )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
theme <- theme( plot.title=element_text( hjust = 0.5, size = 28, face='bold' ) )

fundamentalGraphData <- mainPlot + xScaleConfig + yLimit + xLabel + yLabel + fillLabel + theme


print( "Generating bar graph with error bars." )
width <- 0.9
barGraphFormat <- geom_bar( stat="identity", position=position_dodge( ), width = width )
errorBarFormat <- geom_errorbar( position=position_dodge( ), width = width )
title <- ggtitle( paste( chartTitle, "with Standard Error Bars" ) )
result <- fundamentalGraphData + barGraphFormat + errorBarFormat + title


print( paste( "Saving bar chart with error bars to", errBarOutputFile ) )
ggsave( errBarOutputFile, width = 10, height = 6, dpi = 200 )


print( paste( "Successfully wrote bar chart with error bars out to", errBarOutputFile ) )


print( "Generating stacked bar chart." )
stackedBarFormat <- geom_bar( stat="identity", width=width )
title <- ggtitle( paste( chartTitle, "Total Latency" ) )
result <- fundamentalGraphData + stackedBarFormat + title


print( paste( "Saving stacked bar chart to", stackedBarOutputFile ) )
ggsave( stackedBarOutputFile, width = 10, height = 6, dpi = 200 )


print( paste( "Successfully wrote stacked bar chart out to", stackedBarOutputFile ) )