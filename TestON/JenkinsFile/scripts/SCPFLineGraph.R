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

# This is the R script that generates the SCPF front page graphs.

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "STEP 1: Data management." )

# Import libraries to be used for graphing and organizing data, respectively.
# Find out more about ggplot2: https://github.com/tidyverse/ggplot2
#                     reshape2: https://github.com/hadley/reshape
#                     RPostgreSQL: https://code.google.com/archive/p/rpostgresql/
print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# Check if sufficient args are provided.
if ( is.na( args[ 10 ] ) ){
    print( "Usage: Rscript testresultgraph.R <database-host> <database-port> <database-user-id> <database-password> <test-name> <branch-name> <#-dates> <SQL-command> <y-axis> <directory-to-save-graph>" )
    q()  # basically exit(), but in R
}

# Filenames for the output graph include the testname, branch, and the graph type.

outputFile <- paste( args[ 10 ], "SCPF_Front_Page" , sep="" )
outputFile <- paste( outputFile, gsub( " ", "_", args[ 5 ] ), sep="_" )
outputFile <- paste( outputFile, args[ 6 ], sep="_" )
outputFile <- paste( outputFile, args[ 7 ], sep="_" )
outputFile <- paste( outputFile, "dates", sep="-" )
outputFile <- paste( outputFile, "_graph.jpg", sep="" )

# From RPostgreSQL
print( "Reading from databases." )
con <- dbConnect( dbDriver( "PostgreSQL" ), dbname="onostest", host=args[ 1 ], port=strtoi( args[ 2 ] ), user=args[ 3 ],password=args[ 4 ] )

print( "Sending SQL command." )
fileData <- dbGetQuery( con, args[ 8 ] )

# Title of graph based on command line args.
title <- args[ 5 ]

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "STEP 2: Organize data." )

# Create lists c() and organize data into their corresponding list.
print( "Sorting data into new data frame." )

if ( ncol( fileData ) > 1 ){
    for ( i in 2:ncol( fileData ) ){
        fileData[ i ] <- fileData[ i - 1 ] + fileData[ i ]
    }
}

# Parse lists into data frames.
# This is where reshape2 comes in. Avgs list is converted to data frame.
dataFrame <- melt( fileData )

dataFrame$date <- fileData$date

colnames( dataFrame ) <- c( "Legend", "Values" )

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$Legend <- as.character( dataFrame$Legend )
dataFrame$Legend <- factor( dataFrame$Legend, levels=unique( dataFrame$Legend ) )

# Adding a temporary iterative list to the dataFrame so that there are no gaps in-between date numbers.
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
#        - x: x-axis values (usually iterative, but it will become date # later)
#        - y: y-axis values (usually tests)
#        - color: the category of the colored lines (usually legend of test)
theme_set( theme_grey( base_size = 20 ) )   # set the default text size of the graph.
mainPlot <- ggplot( data = dataFrame, aes( x = iterative, y = Values, color = Legend ) )

print( "Formatting main plot." )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot + expand_limits( y = 0 )

yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$Values ) * 1.05, by = ceiling( max( dataFrame$Values ) / 10 ) ) )

xLabel <- xlab( "Date" )
yLabel <- ylab( args[ 9 ] )
fillLabel <- labs( fill="Type" )
legendLabels <- scale_colour_discrete( labels = names( fileData ) )
centerTitle <- theme( plot.title=element_text( hjust = 0.5 ) )  # To center the title text
theme <- theme( axis.text.x = element_blank(), axis.ticks.x = element_blank(), plot.title = element_text( size = 28, face='bold' ) )

fundamentalGraphData <- fundamentalGraphData + yScaleConfig + xLabel + yLabel + fillLabel + legendLabels + centerTitle + theme
print( "Generating line graph." )

lineGraphFormat <- geom_line()
pointFormat <- geom_point( size = 0.2 )
title <- ggtitle( title )

result <- fundamentalGraphData + lineGraphFormat + pointFormat + title

# Save graph to file
print( paste( "Saving result graph to", outputFile ) )
ggsave( outputFile, width = 10, height = 6, dpi = 200 )
print( paste( "Successfully wrote result graph out to", outputFile ) )