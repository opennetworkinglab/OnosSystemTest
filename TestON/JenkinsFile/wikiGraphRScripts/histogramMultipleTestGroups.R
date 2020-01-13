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
# Example script:
# ALL tests (https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/ALL_master_build-latest_test-suite-summary.jpg):
# Rscript histogramMultipleTestGroups.R <url> <port> <username> <pass> ALL master "FUNCbgpls,FUNCflow,FUNCformCluster,FUNCgroup,FUNCintent,FUNCintentRest,FUNCipv6Intent,FUNCnetCfg,FUNCnetconf,FUNCoptical,FUNCovsdbtest,FUNCvirNetNB,HAbackupRecover,HAclusterRestart,HAfullNetPartition,HAkillNodes,HAsanity,HAscaling,HAsingleInstanceRestart,HAstopNodes,HAswapNodes,HAupgrade,HAupgradeRollback,PLATdockertest,USECASE_SdnipFunction,USECASE_SdnipFunctionCluster,VPLSBasic,VPLSfailsafe" latest /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

testsToInclude <- 7
build_to_show <- 8
save_directory <- 9

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

if ( length( args ) != save_directory ){
    specialArgs <- c( "tests-to-include-(as-one-string-sep-groups-by-semicolon-title-as-first-group-item-sep-by-dash)",
                      "build-to-show" )
    usage( "histogramMultipleTestGroups.R", specialArgs )
    quit( status = 1 )
}

# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ---------------------
# Test Case SQL Command
# ---------------------

print( "Generating Test Case SQL command." )

sqlCommands <- generateGroupedTestSingleBuildSQLCommand( args[ branch_name ],
                                                         args[ testsToInclude ],
                                                         args[ build_to_show ] )

titles <- getTitlesFromGroupTest( args[ branch_name ],
                                  args[ testsToInclude ] )

dbResults <- list()
i <- 1
for ( command in sqlCommands ){
    dbResults[[i]] <- retrieveData( con, command )
    i <- i + 1
}

print( "dbResult:" )
print( dbResults )

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

titlePrefix <- paste( args[ graph_title ], " ", sep="" )
if ( args[ graph_title ] == "ALL" ){
    titlePrefix <- ""
}

if ( args[ build_to_show ] == "latest" ){
    buildTitle <- "\nLatest Test Results"
    filebuild_to_show <- "latest"
} else {
    buildTitle <- paste( " \n Build #", args[ build_to_show ], sep="" )
    filebuild_to_show <- args[ build_to_show ]
}

title <- paste( titlePrefix,
                "Summary of Test Suites - ",
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
                     "_test-suite-summary.jpg",
                     sep="" )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

passNum <- list()
failNum <- list()
exeNum <- list()
skipNum <- list()
totalNum <- list()

passPercent <- list()
failPercent <- list()
exePercent <- list()
nonExePercent <- list()

actualPassPercent <- list()
actualFailPercent <- list()

appName <- c()
afpName <- c()
nepName <- c()

tmpPos <- c()
tmpCases <- c()

for ( i in 1:length( dbResults ) ){
    t <- dbResults[[i]]

    passNum[[i]] <- sum( t$num_passed )
    failNum[[i]] <- sum( t$num_failed )
    exeNum[[i]] <- passNum[[i]] + failNum[[i]]
    totalNum[[i]] <- sum( t$num_planned )
    skipNum[[i]] <- totalNum[[i]] - exeNum[[i]]

    passPercent[[i]] <- passNum[[i]] / exeNum[[i]]
    failPercent[[i]] <- failNum[[i]] / exeNum[[i]]
    exePercent[[i]] <- exeNum[[i]] / totalNum[[i]]
    nonExePercent[[i]] <- ( 1 - exePercent[[i]] ) * 100

    actualPassPercent[[i]] <- passPercent[[i]] * exePercent[[i]] * 100
    actualFailPercent[[i]] <- failPercent[[i]] * exePercent[[i]] * 100

    appName <- c( appName, "Passed" )
    afpName <- c( afpName, "Failed" )
    nepName <- c( nepName, "Skipped/Unexecuted" )

    tmpPos <- c( tmpPos, 100 - ( nonExePercent[[i]] / 2 ), actualPassPercent[[i]] + actualFailPercent[[i]] - ( actualFailPercent[[i]] / 2 ), actualPassPercent[[i]] - ( actualPassPercent[[i]] / 2 ) )
    tmpCases <- c( tmpCases, skipNum[[i]], failNum[[i]], passNum[[i]] )
}

relativePosLength <- length( dbResults ) * 3

relativePos <- c()
relativeCases <- c()

for ( i in 1:3 ){
    relativePos <- c( relativePos, tmpPos[ seq( i, relativePosLength, 3 ) ] )
    relativeCases <- c( relativeCases, tmpCases[ seq( i, relativePosLength, 3 ) ] )
}
names( actualPassPercent ) <- appName
names( actualFailPercent ) <- afpName
names( nonExePercent ) <- nepName

labels <- paste( titles, "\n", totalNum, " Test Cases", sep="" )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing Data Frame" )

dataFrame <- melt( c( nonExePercent, actualFailPercent, actualPassPercent ) )
dataFrame$title <- seq( 1, length( dbResults ), by = 1 )
colnames( dataFrame ) <- c( "perc", "key", "suite" )

dataFrame$xtitles <- labels
dataFrame$relativePos <- relativePos
dataFrame$relativeCases <- relativeCases
dataFrame$valueDisplay <- c( paste( round( dataFrame$perc, digits = 2 ), "% - ", relativeCases, " Tests", sep="" ) )

dataFrame$key <- factor( dataFrame$key, levels=unique( dataFrame$key ) )

dataFrame$willDisplayValue <- dataFrame$perc > 15.0 / length( dbResults )

for ( i in 1:nrow( dataFrame ) ){
    if ( relativeCases[[i]] == "1" ){
        dataFrame[ i, "valueDisplay" ] <- c( paste( round( dataFrame$perc[[i]], digits = 2 ), "% - ", relativeCases[[i]], " Test", sep="" ) )
    }
    if ( !dataFrame[ i, "willDisplayValue" ] ){
        dataFrame[ i, "valueDisplay" ] <- ""
    }
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

mainPlot <- ggplot( data = dataFrame, aes( x = suite,
                                           y = perc,
                                           fill = key ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.

xScaleConfig <- scale_x_continuous( breaks = dataFrame$suite,
                                    label = dataFrame$xtitles )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, 100,
                                    by = 10 ) )

xLabel <- xlab( "" )
yLabel <- ylab( "Total Test Cases (%)" )

theme <- graphTheme() + theme( axis.text.x = element_text( angle = 0, size = 25 - 1.25 * length( dbResults ) ) )

title <- labs( title = title, subtitle = lastUpdatedLabel( Sys.time() ) )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        yScaleConfig +
                        xLabel +
                        yLabel +
                        theme +
                        title

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph." )

unexecutedColor <- webColor( "gray" )   # Gray
failedColor <- webColor( "red" )        # Red
passedColor <- webColor( "green" )      # Green

colors <- scale_fill_manual( values=c( if ( "Skipped/Unexecuted" %in% dataFrame$key ){ unexecutedColor },
                                       if ( "Failed" %in% dataFrame$key ){ failedColor },
                                       if ( "Passed" %in% dataFrame$key ){ passedColor } ) )

barGraphFormat <- geom_bar( stat = "identity", width = 0.8 )

barGraphValues <- geom_text( aes( x = dataFrame$suite,
                                  y = dataFrame$relativePos,
                                  label = format( paste( dataFrame$valueDisplay ) ) ),
                                  size = 15.50 / length( dbResults ) + 2.33, fontface = "bold" )

result <- fundamentalGraphData +
          colors +
          barGraphFormat +
          barGraphValues

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( outputFile ) # from saveGraph.R
