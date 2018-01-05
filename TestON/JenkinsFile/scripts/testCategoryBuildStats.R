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
buildToShow <- 8
displayStatus <- 9
scaleOfPercent <- 10
saveDirectory <- 11

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
                                  "<build-to-show>",
                                  "<pass/fail/plan>",
                                  "<percent-scale>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )

    quit( status = 1 )  # basically exit(), but in R
}

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

fileBuildToShow <- args[ buildToShow ]
operator <- "= "
if ( args[ buildToShow ] == "latest" ){
    operator <- ">= "
    args[ buildToShow ] <- "1000"
}

command <- paste( "SELECT * ",
                  "FROM executed_test_tests a ",
                  "WHERE ( SELECT COUNT( * ) FROM executed_test_tests b ",
                  "WHERE b.branch='",
                  args[ branchName ],
                  "' AND b.actual_test_name IN (",
                  tests,
                  ") AND a.actual_test_name = b.actual_test_name AND a.date <= b.date AND b.build ", operator,
                  args[ buildToShow ],
                  " ) = ",
                  1,
                  " AND a.branch='",
                  args[ branchName ],
                  "' AND a.actual_test_name IN (",
                  tests,
                  ") AND a.build ", operator,
                  args[ buildToShow ],
                  " ORDER BY a.actual_test_name DESC, a.date DESC",
                  sep="")

print( "Sending SQL command:" )
print( command )
dbResult <- dbGetQuery( con, command )

maxBuild <- max( dbResult[ 'build' ] )
dbResult <- dbResult[ which( dbResult[,4]>=maxBuild ), ]

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

titleDisplayStatus <- ""
if ( args[ displayStatus ] == "fail" ){
    titleDisplayStatus <- "Failed"
} else if ( args[ displayStatus ] == "plan" ){
    titleDisplayStatus <- "Executed"
} else if ( args[ displayStatus ] == "pass" ){
    titleDisplayStatus <- "Succeeded"
} else {
    print( paste( "[ERROR]: Invalid histogram display status: ", args[ displayStatus ], sep="" ) )
    quit( status = 1 )
}

title <- paste( args[ testSuiteName ],
                " Tests ",
                titleDisplayStatus,
                " - ",
                args[ branchName ],
                " \n Build #",
                max( dbResult[ 'build' ] ),
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ saveDirectory ],
                     args[ testSuiteName ],
                     "_",
                     args[ branchName ],
                     "_build-",
                     fileBuildToShow,
                     "_",
                     args[ scaleOfPercent ],
                     "-scaling",
                     "_",
                     args[ displayStatus ],
                     "_histogram.jpg",
                     sep="" )

print( dbResult )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

t <- subset( dbResult, select=c( "actual_test_name", "num_passed", "num_failed", "num_planned" ) )
t$passed_percent <- t$num_passed / t$num_planned * 100
t$failed_percent <- t$num_failed / t$num_planned * 100
t$planned_percent <- ( t$num_passed + t$num_failed ) / t$num_planned * 100

# --------------------
# Construct Data Frame
# --------------------

dataFrame <- aggregate( t$passed_percent, by=list( Category=t$actual_test_name ), FUN=sum )
if ( args[ displayStatus ] == "fail" ){
    dataFrame <- aggregate( t$failed_percent, by=list( Category=t$actual_test_name ), FUN=sum )
} else if ( args[ displayStatus ] == "plan" ){
    dataFrame <- aggregate( t$planned_percent, by=list( Category=t$actual_test_name ), FUN=sum )
}

colnames( dataFrame ) <- c( "Test", paste( titleDisplayStatus, "%", sep="" ) )

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

mainPlot <- ggplot( data = dataFrame, aes( dataFrame[ ,2 ] ) )

# -------------------
# Main Plot Formatted
# -------------------

print( "Formatting main plot." )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.

xScaleConfig <- scale_x_continuous( breaks = seq( 0, 100, by = 10 ) )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, nrow( dbResult ), by = 1 ), limits = c( 0, nrow( dbResult ) ) )

xLabel <- xlab( paste( titleDisplayStatus, "%" ) )
yLabel <- ylab( "Frequency" )

imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

# Set other graph configurations here.
theme <- theme( plot.title = element_text( hjust = 0.5, size = 32, face ='bold' ),
                axis.text.x = element_text( angle = 0, size = 14 ),
                legend.position = "bottom",
                legend.text = element_text( size = 22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ),
                plot.subtitle = element_text( size=16, hjust=1.0 ) )

subtitle <- paste( "Last Updated: ", format( Sys.time(), format = "%b %d, %Y at %I:%M %p %Z" ), sep="" )

title <- labs( title = title, subtitle = subtitle )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        yScaleConfig +
                        xLabel +
                        yLabel +
                        theme +
                        title

# ----------------------------
# Generating Line Graph Format
# ----------------------------

print( "Generating line graph." )

barColor <- "#00B208"
if ( args[ displayStatus ] == "fail" ){
    barColor <- "#E80000"
} else if ( args[ displayStatus ] == "plan" ){
    barColor <- "#00A5FF"
}

histogramFormat <- geom_histogram( col = "#000000",
                                   fill = barColor,
                                   breaks = seq( 0, 100, by = strtoi( args[ scaleOfPercent ] ) ),
                                   lwd = 0.5 )

result <- fundamentalGraphData +
           histogramFormat

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
