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
# Example script:
# FUNC Test Results Trend (https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/FUNC_master_overview.jpg):
# Rscript trendMultipleTests.R <url> <port> <username> <pass> FUNC master "FUNCflow,FUNCformCluster,FUNCgroup,FUNCintent,FUNCintentRest,FUNCipv6Intent,FUNCnetCfg,FUNCnetconf,FUNCoptical,FUNCovsdbtest" 20 /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

tests_to_include <- 7
builds_to_show <- 8
save_directory <- 9

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )
source( "dependencies/saveGraph.R" )
source( "dependencies/fundamentalGraphData.R" )
source( "dependencies/initSQL.R" )
source( "dependencies/cliArgs.R" )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

args <- commandArgs( trailingOnly=TRUE )

if ( length( args ) != save_directory ){
    specialArgs <- c(  "tests-to-include-(as-one-string)",
                       "builds-to-show" )
    usage( "trendMultipleTests.R", specialArgs )
    quit( status = 1 )
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

title <- paste( args[ graph_title ],
                " Test Results Trend - ",
                args[ branch_name ],
                " \n Results of Last ",
                args[ builds_to_show ],
                " Nightly Builds",
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ save_directory ],
                     args[ graph_title ],
                     "_",
                     args[ branch_name ],
                     "_overview.jpg",
                     sep="" )

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

command <- generateMultiTestMultiBuildSQLCommand( args[ branch_name ],
                                                  args[ tests_to_include ],
                                                  args[ builds_to_show ] )

dbResult <- retrieveData( con, command )
maxBuild <- max( dbResult[ 'build' ] ) - strtoi( args[ builds_to_show ] )
dbResult <- dbResult[ which( dbResult[,4] > maxBuild ), ]

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
                                 fill = webColor( "red" ),
                                 linetype = 0,
                                 alpha = 0.07 )

passedColor <- geom_ribbon( aes( ymin = 0,
                                 ymax = dataFrame$num_passed ),
                                 fill = webColor( "light_blue" ),
                                 linetype = 0,
                                 alpha = 0.05 )

plannedColor <- geom_ribbon( aes( ymin = 0,
                                  ymax = dataFrame$num_planned ),
                                  fill = webColor( "black" ),
                                  linetype = 0,
                                  alpha = 0.01 )

# Colors for the lines
lineColors <- scale_color_manual( values=c( webColor( "red" ),
                                            webColor( "light_blue" ),
                                            webColor( "black" )),
                                  labels = c( "Containing Failures",
                                              "No Failures",
                                              "Total Built" ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

defaultTextSize()

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$build )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$results ),
                                    by = ceiling( max( dataFrame$results ) / 10 ) ) )

xLabel <- xlab( "Build Number" )
yLabel <- ylab( "Tests" )

theme <- graphTheme()

title <- labs( title = title, subtitle = lastUpdatedLabel() )

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

saveGraph( outputFile )
