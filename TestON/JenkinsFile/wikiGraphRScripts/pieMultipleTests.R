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
# Example scripts:
#
# ALL tests with pass/fail (https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/ALL_master_build-latest_executed_pieChart.jpg):
# Rscript pieMultipleTests.R <url> <port> <username> <pass> ALL master "FUNCbgpls,FUNCflow,FUNCformCluster,FUNCgroup,FUNCintent,FUNCintentRest,FUNCipv6Intent,FUNCnetCfg,FUNCnetconf,FUNCoptical,FUNCovsdbtest,FUNCvirNetNB,HAbackupRecover,HAclusterRestart,HAfullNetPartition,HAkillNodes,HAsanity,HAscaling,HAsingleInstanceRestart,HAstopNodes,HAswapNodes,HAupgrade,HAupgradeRollback,PLATdockertest,USECASE_SdnipFunction,USECASE_SdnipFunctionCluster,VPLSBasic,VPLSfailsafe" latest y /path/to/save/directory/
#
# ALL tests with execution result (https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/ALL_master_build-latest_passfail_pieChart.jpg):
# Rscript pieMultipleTests.R <url> <port> <username> <pass> ALL master "FUNCbgpls,FUNCflow,FUNCformCluster,FUNCgroup,FUNCintent,FUNCintentRest,FUNCipv6Intent,FUNCnetCfg,FUNCnetconf,FUNCoptical,FUNCovsdbtest,FUNCvirNetNB,HAbackupRecover,HAclusterRestart,HAfullNetPartition,HAkillNodes,HAsanity,HAscaling,HAsingleInstanceRestart,HAstopNodes,HAswapNodes,HAupgrade,HAupgradeRollback,PLATdockertest,USECASE_SdnipFunction,USECASE_SdnipFunctionCluster,VPLSBasic,VPLSfailsafe" latest n /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

tests_to_include <- 7
build_to_show <- 8
is_displaying_plan <- 9
save_directory <- 10

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

if ( is.na( args[ save_directory ] ) ){

    # Check if sufficient args are provided.
    if ( length( args ) != save_directory ){
        specialArgs <- c(  "tests-to-include",
                           "build-to-show",
                           "is-displaying-plan" )
        usage( "trendSCPF.R", specialArgs )
        quit( status = 1 )
    }
}

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

# ---------------------
# Test Case SQL Command
# ---------------------

print( "Generating Test Case SQL command." )

command <- generateMultiTestSingleBuildSQLCommand( args[ branch_name ],
                                                   args[ tests_to_include ],
                                                   args[ build_to_show ] )

dbResult <- retrieveData( con, command )

print( "dbResult:" )
print( dbResult )

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

typeOfPieTitle <- "Executed Results"
typeOfPieFile <- "_passfail"
isPlannedPie <- FALSE
if ( args[ is_displaying_plan ] == "y" ){
    typeOfPieTitle <- "Test Execution"
    typeOfPieFile <- "_executed"
    isPlannedPie <- TRUE
}

if ( args[ build_to_show ] == "latest" ){
    buildTitle <- "\nLatest Test Results"
    filebuild_to_show <- "latest"
} else {
    buildTitle <- paste( " \n Build #", args[ build_to_show ], sep="" )
    filebuild_to_show <- args[ build_to_show ]
}

title <- paste( args[ graph_title ],
                " Tests: Summary of ",
                typeOfPieTitle,
                "",
                " - ",
                args[ branch_name ],
                buildTitle,
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ save_directory ],
                     args[ graph_title ],
                     "_",
                     args[ branch_name ],
                     "_build-",
                     filebuild_to_show,
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

defaultTextSize()

# Set other graph configurations here.
theme <- graphTheme() +
         theme( axis.text.x = element_blank(),
                axis.title.x = element_blank(),
                axis.title.y = element_blank(),
                axis.ticks = element_blank(),
                panel.border = element_blank(),
                panel.grid=element_blank(),
                legend.position = "bottom" )

title <- labs( title = title, subtitle = lastUpdatedLabel() )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        theme +
                        title

# ----------------------------
# Generating Line Graph Format
# ----------------------------

print( "Generating line graph." )

if ( isPlannedPie ){
    executedColor <- webColor( "light_blue" )
    nonExecutedColor <- webColor( "gray" )
    pieColors <- scale_fill_manual( values = c( executedColor, nonExecutedColor ) )
} else {
    passColor <- webColor( "green" )
    failColor <- webColor( "red" )
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

saveGraph( outputFile )
