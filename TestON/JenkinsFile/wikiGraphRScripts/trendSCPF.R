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

# Args 1 through 6 reside in fundamentalGraphData.R
num_dates = 7
sql_commands = 8
y_axis = 9
old_flow = 10
save_directory = 11

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/saveGraph.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/fundamentalGraphData.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/initSQL.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/cliArgs.R" )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

args <- commandArgs( trailingOnly=TRUE )

# Check if sufficient args are provided.
if ( length( args ) != save_directory ){
    specialArgs <- c(  "#-dates",
                       "SQL-command",
                       "y-axis-title",
                       "using-old-flow" )
    usage( "trendSCPF.R", specialArgs )
    quit( status = 1 )
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph" )

# Title of graph based on command line args.

title <- args[ graph_title ]
title <- paste( title, if( args[ old_flow ] == "y" ) "\nWith Eventually Consistent Flow Rule Store" else "" )

print( "Creating graph filename." )

# Filenames for the output graph include the testname, branch, and the graph type.
outputFile <- paste( args[ save_directory ],
                    "SCPF_Front_Page_",
                    gsub( " ", "_", args[ graph_title ] ),
                    "_",
                    args[ branch_name ],
                    "_",
                    args[ num_dates ],
                    "-dates",
                    if( args[ old_flow ] == "y" ) "_OldFlow" else "",
                    "_graph.jpg",
                    sep="" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )
con <- initSQL( args[ database_host ], args[ database_port ], args[ database_u_id ], args[ database_pw ] )

fileData <- retrieveData( con, args[ sql_commands ] )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

latestBuildDate <- fileData$date[1]

# Create lists c() and organize data into their corresponding list.
print( "Combine data retrieved from databases into a list." )

buildNums <- fileData$build
fileData$build <- c()
fileData <- subset( fileData, select=-c( date ) )
print( fileData )

if ( ncol( fileData ) > 1 ){
    for ( i in 2:ncol( fileData ) ){
        fileData[ i ] <- fileData[ i - 1 ] + fileData[ i ]
    }
}


# --------------------
# Construct Data Frame
# --------------------

print( "Constructing data frame from combined data." )

dataFrame <- melt( fileData )
dataFrame$date <- fileData$date

colnames( dataFrame ) <- c( "Legend",
                            "Values" )

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$Legend <- as.character( dataFrame$Legend )
dataFrame$Legend <- factor( dataFrame$Legend, levels=unique( dataFrame$Legend ) )
dataFrame$build <- buildNums

# Adding a temporary iterative list to the dataFrame so that there are no gaps in-between date numbers.
dataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

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
#        - x: x-axis values (usually iterative, but it will become date # later)
#        - y: y-axis values (usually tests)
#        - color: the category of the colored lines (usually legend of test)

mainPlot <- ggplot( data = dataFrame, aes( x = iterative,
                                           y = Values,
                                           color = Legend ) )

# -------------------
# Main Plot Formatted
# -------------------

print( "Formatting main plot." )

limitExpansion <- expand_limits( y = 0 )

tickLength <- 3
breaks <- seq( max( dataFrame$iterative ) %% tickLength, max( dataFrame$iterative ), by = tickLength )
breaks <- breaks[ which( breaks != 0 ) ]

maxYDisplay <- max( dataFrame$Values ) * 1.05
yBreaks <- ceiling( max( dataFrame$Values ) / 10 )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, maxYDisplay, by = yBreaks ) )
xScaleConfig <- scale_x_continuous( breaks = breaks, label = rev( dataFrame$build )[ breaks ] )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

defaultTextSize()
xLabel <- xlab( "Build" )
yLabel <- ylab( args[ y_axis ] )

# Set other graph configurations here.
theme <- graphTheme()

title <- labs( title = title, subtitle = lastUpdatedLabel( latestBuildDate ) )

# Colors used for the lines.
# Note: graphs that have X lines will use the first X colors in this list.
colors <- scale_color_manual( values=c( webColor( "black" ),   # black
                                        webColor( "blue" ),   # blue
                                        webColor( "red" ),   # red
                                        webColor( "green" ),   # green
                                        webColor( "yellow" ),   # yellow
                                        webColor( "purple" ) ) ) # purple (not used)

wrapLegend <- wrapLegend()

fundamentalGraphData <- mainPlot +
                        limitExpansion +
                        xScaleConfig +
                        yScaleConfig +
                        xLabel +
                        yLabel +
                        theme +
                        colors +
                        wrapLegend +
                        title

# ----------------------------
# Generating Line Graph Format
# ----------------------------

print( "Generating line graph." )

lineGraphFormat <- geom_line( size = 0.75 )
pointFormat <- geom_point( size = 1.75 )

result <- fundamentalGraphData +
          lineGraphFormat +
          pointFormat

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( outputFile ) # from saveGraph.R
quit( status = 0 )
