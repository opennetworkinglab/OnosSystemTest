# Copyright 2018 Open Networking Foundation (ONF)
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
isDisplayingPlan <- 9
saveDirectory <- 10

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

    print( paste( "Usage: Rscript testCategoryPiePassFail.R",
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-suite-name>",
                                  "<branch-name>",
                                  "<tests-to-include-(as-one-string)>",
                                  "<build-to-show>",
                                  "<is-displaying-plan>",
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
buildTitle <- ""
if ( args[ buildToShow ] == "latest" ){
    buildTitle <- "\nLatest Test Results"
    operator <- ">= "
    args[ buildToShow ] <- "1000"
} else {
    buildTitle <- paste( " \n Build #", args[ buildToShow ], sep="" )
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

print( "dbResult:" )
print( dbResult )

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

typeOfPieTitle <- "Executed Results"
typeOfPieFile <- "_passfail"
isPlannedPie <- FALSE
if ( args[ isDisplayingPlan ] == "y" ){
    typeOfPieTitle <- "Test Execution"
    typeOfPieFile <- "_executed"
    isPlannedPie <- TRUE
}

title <- paste( args[ testSuiteName ],
                " Tests: Summary of ",
                typeOfPieTitle,
                "",
                " - ",
                args[ branchName ],
                buildTitle,
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ saveDirectory ],
                     args[ testSuiteName ],
                     "_",
                     args[ branchName ],
                     "_build-",
                     fileBuildToShow,
                     typeOfPieFile,
                     "_pieChart.jpg",
                     sep="" )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

t <- subset( dbResult, select=c( "actual_test_name", "num_passed", "num_failed", "num_planned" ) )

executedTests <- sum( t$num_passed ) + sum( t$num_failed )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing Data Frame." )

if ( isPlannedPie ){

    nonExecutedTests <- sum( t$num_planned ) - executedTests
    totalTests <- sum( t$num_planned )

    executedPercent <- round( executedTests / totalTests * 100, digits = 2 )
    nonExecutedPercent <- 100 - executedPercent

    dfData <- c( nonExecutedPercent, executedPercent )

    labels <- c( "Executed Test Cases", "Skipped Test Cases" )

    dataFrame <- data.frame(
        rawData <- dfData,
        displayedData <- c( paste( nonExecutedPercent, "%\n", nonExecutedTests, " / ", totalTests, " Tests", sep="" ), paste( executedPercent, "%\n", executedTests, " / ", totalTests," Tests", sep="" ) ),
        names <- factor( rev( labels ), levels = labels ) )
} else {

    sumPassed <- sum( t$num_passed )
    sumFailed <- sum( t$num_failed )
    sumExecuted <- sumPassed + sumFailed

    percentPassed <- sumPassed / sumExecuted
    percentFailed <- sumFailed / sumExecuted

    dfData <- c( percentFailed, percentPassed )
    labels <- c( "Failed Test Cases", "Passed Test Cases" )

    dataFrame <- data.frame(
        rawData <- dfData,
        displayedData <- c( paste( round( percentFailed * 100, 2 ), "%\n", sumFailed, " / ", sumExecuted, " Tests", sep="" ), paste( round( percentPassed * 100, 2 ), "%\n", sumPassed, " / ", sumExecuted, " Tests", sep="" ) ),
        names <- factor( labels, levels = rev( labels ) ) )
}

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

mainPlot <- ggplot( data = dataFrame,
                    aes( x = "", y=rawData, fill = names ) )

# -------------------
# Main Plot Formatted
# -------------------

print( "Formatting main plot." )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.

imageWidth <- 12
imageHeight <- 10
imageDPI <- 200

# Set other graph configurations here.
theme <- theme( plot.title = element_text( hjust = 0.5, size = 30, face ='bold' ),
                axis.text.x = element_blank(),
                axis.title.x = element_blank(),
                axis.title.y = element_blank(),
                axis.ticks = element_blank(),
                panel.border = element_blank(),
                panel.grid=element_blank(),
                legend.position = "bottom",
                legend.text = element_text( size = 22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ),
                plot.subtitle = element_text( size=16, hjust=1.0 ) )

subtitle <- paste( "Last Updated: ", format( Sys.time(), format = "%b %d, %Y at %I:%M %p %Z" ), sep="" )

title <- labs( title = title, subtitle = subtitle )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        theme +
                        title

# ----------------------------
# Generating Line Graph Format
# ----------------------------

print( "Generating line graph." )

if ( isPlannedPie ){
    executedColor <- "#00A5FF"      # Blue
    nonExecutedColor <- "#CCCCCC"   # Gray
    pieColors <- scale_fill_manual( values = c( executedColor, nonExecutedColor ) )
} else {
    passColor <- "#16B645"          # Green
    failColor <- "#E02020"          # Red
    pieColors <- scale_fill_manual( values = c( passColor, failColor ) )
}

pieFormat <- geom_bar( width = 1, stat = "identity" )
pieLabels <- geom_text( aes( y = rawData / length( rawData ) + c( 0, cumsum( rawData )[ -length( rawData ) ] ) ),
                             label = dataFrame$displayedData,
                             size = 7, fontface = "bold" )


result <- fundamentalGraphData +
          pieFormat + coord_polar( "y" ) + pieLabels + pieColors
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
