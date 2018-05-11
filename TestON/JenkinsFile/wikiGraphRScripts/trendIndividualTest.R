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
# FUNCintent Results 20 Builds (https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/FUNCintent_master_20-builds_graph.jpg):
# Rscript trendIndividualTest.R <url> <port> <username> <pass> FUNCintent master 20 /path/to/save/directory/


# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# Args 1 through 6 reside in fundamentalGraphData.R
buildsToShow <- 7
save_directory <- 8

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
    specialArgs <- c(  "#-builds-to-show" )
    usage( "trendIndividualTest.R", specialArgs )
    quit( status = 1 )
}

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating title of graph." )

title <- paste( args[ graph_title ],
                " - ",
                args[ branch_name ],
                " \n Results of Last ",
                args[ buildsToShow ],
                " Builds",
                sep="" )

print( "Creating graph filename." )

outputFile <- paste( args[ save_directory ],
                     args[ graph_title ],
                     "_",
                     args[ branch_name ],
                     "_",
                     args[ buildsToShow ],
                     "-builds_graph.jpg",
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

command <- simpleSQLCommand( args[ graph_title ], args[ branch_name ], args[ buildsToShow ] )

fileData <- retrieveData( con, command )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# -------------------------------------------------------
# Combining Passed, Failed, and Planned Data
# -------------------------------------------------------

print( "Combining Passed, Failed, and Planned Data." )

requiredColumns <- c( "num_failed", "num_passed", "num_planned" )

tryCatch( categories <- c( fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from the data. Please check that the data and SQL command are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing data frame from combined data." )

dataFrame <- melt( categories )

# Rename column names in dataFrame
colnames( dataFrame ) <- c( "Tests",
                            "Status" )

# Add build dates to the dataFrame
dataFrame$build <- fileData$build

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$Status <- as.character( dataFrame$Status )
dataFrame$Status <- factor( dataFrame$Status, levels = unique( dataFrame$Status ) )

# Add planned, passed, and failed results to the dataFrame (for the fill below the lines)
dataFrame$num_planned <- fileData$num_planned
dataFrame$num_passed <- fileData$num_passed
dataFrame$num_failed <- fileData$num_failed

# Adding a temporary reversed iterative list to the dataFrame so that there are no gaps in-between build numbers.
dataFrame$iterative <- rev( seq( 1, nrow( fileData ), by = 1 ) )

# Omit any data that doesn't exist
dataFrame <- na.omit( dataFrame )

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

mainPlot <- ggplot( data = dataFrame, aes( x = iterative,
                                           y = Tests,
                                           color = Status ) )

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
                                 fill = webColor( "green" ),
                                 linetype = 0,
                                 alpha = 0.05 )

plannedColor <- geom_ribbon( aes( ymin = 0,
                                  ymax = dataFrame$num_planned ),
                                  fill = webColor( "blue" ),
                                  linetype = 0,
                                  alpha = 0.01 )

# Colors for the lines
lineColors <- scale_color_manual( values=c( webColor( "red" ),
                                            webColor( "green" ),
                                            webColor( "blue" ) ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

defaultTextSize()

xScaleConfig <- scale_x_continuous( breaks = dataFrame$iterative,
                                    label = dataFrame$build )
yScaleConfig <- scale_y_continuous( breaks = seq( 0, max( dataFrame$Tests ),
                                    by = ceiling( max( dataFrame$Tests ) / 10 ) ) )

xLabel <- xlab( "Build Number" )
yLabel <- ylab( "Test Cases" )

legendLabels <- scale_colour_discrete( labels = c( "Failed Cases",
                                                   "Passed Cases",
                                                   "Planned Cases" ) )

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
                        lineColors +
                        legendLabels +
                        graphTheme() +  # from fundamentalGraphData.R
                        title

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

saveGraph( outputFile ) # from saveGraph.R
