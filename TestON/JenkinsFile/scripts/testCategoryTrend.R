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

pipelineMinValue = 1000

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

databaseHost <- 1
databasePort <- 2
databaseUserID <- 3
databasePassword <- 4
testSuiteName <- 5
branchName <- 6
testsToInclude <- 7
buildsToShow <- 8
saveDirectory <- 9

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

if ( is.na( args[ saveDirectory ] ) ){

    print( paste( "Usage: Rscript testCategoryTrend.R",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-suite-name>",
                                  "<branch-name>",
                                  "<tests-to-include-(as-one-string)>",
                                  "<builds-to-show>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    quit( status = 1 )  # basically exit(), but in R
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

title <- paste( args[ testSuiteName ],
                " Test Results Trend - ",
                args[ branchName ],
                " \n Results of Last ",
                args[ buildsToShow ],
                " Nightly Builds",
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ saveDirectory ],
                     args[ testSuiteName ],
                     "_",
                     args[ branchName ],
                     "_overview.jpg",
                     sep="" )

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- dbConnect( dbDriver( "PostgreSQL" ),
                  dbname = "onostest",
                  host = args[ databaseHost ],
                  port = strtoi( args[ databasePort ] ),
                  user = args[ databaseUserID ],
                  password = args[ databasePassword ] )

# ---------------------
# Test Case SQL Command
# ---------------------
print( "Generating Test Case SQL command." )

tests <- "'"
for ( test in as.list( strsplit( args[ testsToInclude ], "," )[[1]] ) ){
    tests <- paste( tests, test, "','", sep="" )
}
tests <- substr( tests, 0, nchar( tests ) - 2 )

command <- paste( "SELECT * ",
                  "FROM executed_test_tests a ",
                  "WHERE ( SELECT COUNT( * ) FROM executed_test_tests b ",
                  "WHERE b.branch='",
                  args[ branchName ],
                  "' AND b.actual_test_name IN (",
                  tests,
                  ") AND a.actual_test_name = b.actual_test_name AND a.date <= b.date AND b.build >= ",
                  pipelineMinValue,
                  " ) <= ",
                  args[ buildsToShow ],
                  " AND a.branch='",
                  args[ branchName ],
                  "' AND a.actual_test_name IN (",
                  tests,
                  ") AND a.build >= ",
                  pipelineMinValue,
                  " ORDER BY a.actual_test_name DESC, a.date DESC",
                  sep="")

print( "Sending SQL command:" )
print( command )
dbResult <- dbGetQuery( con, command )
maxBuild <- max( dbResult[ 'build' ] ) - strtoi( args[ buildsToShow ] )
dbResult <- dbResult[ which( dbResult[,4]>maxBuild ), ]
print( dbResult )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

t <- subset( dbResult, select=c( "actual_test_name", "build", "num_failed" ) )
t$num_failed <- ceiling( t$num_failed / ( t$num_failed + 1 ) )
t$num_planned <- 1

fileData <- aggregate( t$num_failed, by=list( Category=t$build ), FUN=sum )
colnames( fileData ) <- c( "build", "num_failed" )

fileData$num_planned <- ( aggregate( t$num_planned, by=list( Category=t$build ), FUN=sum ) )$x
fileData$num_passed <- fileData$num_planned - fileData$num_failed

print(fileData)

# --------------------
# Construct Data Frame
# --------------------
#

dataFrame <- melt( subset( fileData, select=c( "num_failed", "num_passed", "num_planned" ) ) )
dataFrame$build <- fileData$build
colnames( dataFrame ) <- c( "status", "results", "build" )

dataFrame$num_failed <- fileData$num_failed
dataFrame$num_passed <- fileData$num_passed
dataFrame$num_planned <- fileData$num_planned
dataFrame$iterative <- seq( 1, nrow( fileData ), by = 1 )

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
                                           y = results,
                                           color = status ) )

# -------------------
# Main Plot Formatted
# -------------------

print( "Formatting main plot." )

# geom_ribbon is used so that there is a colored fill below the lines. These values shouldn't be changed.
failedColor <- geom_ribbon( aes( ymin = 0,
                                 ymax = dataFrame$num_failed ),
                                 fill = "#ff0000",
                                 linetype = 0,
                                 alpha = 0.07 )

passedColor <- geom_ribbon( aes( ymin = 0,
                                 ymax = dataFrame$num_passed ),
                                 fill = "#0083ff",
                                 linetype = 0,
                                 alpha = 0.05 )

plannedColor <- geom_ribbon( aes( ymin = 0,
                                  ymax = dataFrame$num_planned ),
                                  fill = "#000000",
                                  linetype = 0,
                                  alpha = 0.01 )

# Colors for the lines
lineColors <- scale_color_manual( values=c( "#ff0000",      # fail
                                            "#0083ff",      # pass
                                            "#000000"),
                                  labels = c( "Containing Failures",
                                              "No Failures",
                                              "Total Built" ) )    # planned

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$build )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$results ),
                                    by = ceiling( max( dataFrame$results ) / 10 ) ) )

xLabel <- xlab( "Build Number" )
yLabel <- ylab( "Tests" )

imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

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
                        theme +
                        title +
                        lineColors

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

print( paste( "[SUCCESS] Successfully wrote result graph out to", outputFile ) )
quit( status = 0 )
