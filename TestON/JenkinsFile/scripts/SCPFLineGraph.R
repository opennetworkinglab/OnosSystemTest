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

database_host = 1
database_port = 2
database_u_id = 3
database_pw = 4
graph_title = 5
branch_name = 6
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

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# Check if sufficient args are provided.
if ( is.na( args[ save_directory ] ) ){

    print( paste( "Usage: Rscript testresultgraph.R",
                                    "<database-host>",
                                    "<database-port>",
                                    "<database-user-id>",
                                    "<database-password>",
                                    "<graph-title>",    # part of the output filename as well
                                    "<branch-name>",    # part of the output filename
                                    "<#-dates>",        # part of the output filename
                                    "<SQL-command>",
                                    "<y-axis-title>",   # y-axis may be different among other SCPF graphs (ie: batch size, latency, etc. )
                                    "<using-old-flow>",
                                    "<directory-to-save-graph>",
                  sep = " " ) )
    q()  # basically exit(), but in R
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph" )

# Title of graph based on command line args.

title <- args[ graph_title ]
title <- paste( title, if( args[ old_flow ] == "y" ) "\nWith Old Flow" else "" )

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
con <- dbConnect( dbDriver( "PostgreSQL" ),
                  dbname = "onostest",
                  host = args[ database_host ],
                  port = strtoi( args[ database_port ] ),
                  user = args[ database_u_id ],
                  password = args[ database_pw ] )

print( "Sending SQL command:" )
print( args[ sql_commands ] )
fileData <- dbGetQuery( con, args[ sql_commands ] )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# Create lists c() and organize data into their corresponding list.
print( "Combine data retrieved from databases into a list." )

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

maxYDisplay <- max( dataFrame$Values ) * 1.05
yBreaks <- ceiling( max( dataFrame$Values ) / 10 )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, maxYDisplay, by = yBreaks ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 22 ) )   # set the default text size of the graph.
xLabel <- xlab( "Build" )
yLabel <- ylab( args[ y_axis ] )

imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

# Set other graph configurations here.
theme <- theme( axis.text.x = element_blank(),
                axis.ticks.x = element_blank(),
                plot.title = element_text( size = 32, face='bold', hjust = 0.5 ),
                legend.position = "bottom",
                legend.text = element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ),
                legend.direction = 'horizontal' )

# Colors used for the lines.
# Note: graphs that have X lines will use the first X colors in this list.
colors <- scale_color_manual( values=c( "#111111",   # black
                                        "#008CFF",   # blue
                                        "#FF3700",   # red
                                        "#00E043",   # green
                                        "#EEB600",   # yellow
                                        "#E500FF") ) # purple (not used)

wrapLegend <- guides( color = guide_legend( nrow = 2, byrow = TRUE ) )
title <- ggtitle( title )

fundamentalGraphData <- mainPlot +
                        limitExpansion +
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

print( paste( "Saving result graph to", outputFile ) )

ggsave( outputFile,
        width = imageWidth,
        height = imageHeight,
        dpi = imageDPI )

print( paste( "[SUCCESS] Successfully wrote result graph out to", outputFile ) )
