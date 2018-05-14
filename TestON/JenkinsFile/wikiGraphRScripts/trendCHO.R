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
# Rscript trendCHO event.csv failure.csv error.csv master 60 /path/to/save/directory/

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

# Command line arguments are read. Args include the database credentials, test name, branch name, and the directory to output files.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )


limitToDisplayIndividually <- 37    # must be less than this number to display individually

event_input_file <- 1
failure_input_file <- 2
error_input_file <- 3
branch_name <- 4
time_quantum <- 5
maxDataToDisplayParam <- 6             # the maximum amount of data to display on the graph. Last data point is most recent
save_directory <- 7

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/saveGraph.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/fundamentalGraphData.R" )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( length( args ) != save_directory ){
    print( "Usage: Rscript trendCHO.R <events-input-file> <failures-input-file> <errors-input-file> <branch-name> <time_quantum> <max-data-to-display> <directory-to-save-graph>" )
    quit( status = 1 )
}

# ----------------------
# Read From File: Events
# ----------------------

print( "Reading from file for 'events' input." )

event_fileData <- read.delim2( args[ event_input_file ],
                               header = TRUE,
                               sep = ",",
                               dec = "." )
print( "Event File Data:" )
print( event_fileData )

# ------------------------
# Read From File: Failures
# ------------------------

print( "Reading from file for 'failure' input." )

failure_fileData <- read.delim2( args[ failure_input_file ],
                                 header = TRUE,
                                 sep = ",",
                                 dec = "." )
print( "Failure File Data:" )
print( failure_fileData )

# ----------------------
# Read From File: Errors
# ----------------------

print( "Reading from file for 'errors' input." )

error_fileData <- read.delim2( args[ error_input_file ],
                               header = TRUE,
                               sep = ",",
                               dec = "." )
print( "Error File Data:" )
print( error_fileData )

# -------------------------------
# Create Title and Graph Filename
# -------------------------------

print( "Creating titles of graphs." )

failedChecksTitle <- paste( "Failed Checks - ",
                            args[ branch_name ],
                            "\nFrequency per ",
                            args[ time_quantum ],
                            " Minutes - Last ",
                            args[ maxDataToDisplayParam ],
                            " Hours",
                            sep="" )

eventsTitle <- paste( "Network, Application, and ONOS Events - ",
                      args[ branch_name ],
                      "\nFrequency per ",
                      args[ time_quantum ],
                      " Minutes - Last ",
                      args[ maxDataToDisplayParam ],
                      " Hours",
                      sep="" )

errorsTitle <- paste( "Warnings, Errors, and Exceptions from Logs - ",
                      args[ branch_name ],
                      "\nFrequency per ",
                      args[ time_quantum ],
                      " Minutes - Last ",
                      args[ maxDataToDisplayParam ],
                      " Hours",
                      sep="" )

print( "Creating graph filenames." )

failedChecksFilename <- paste( args[ save_directory ],
                            "CHO_Failure-Check_",
                            args[ branch_name ],
                            "_",
                            args[ maxDataToDisplayParam ],
                            "-maxData_graph.jpg",
                            sep="" )

eventsFilename <- paste( args[ save_directory ],
                         "CHO_Events_",
                         args[ branch_name ],
                         "_",
                         args[ maxDataToDisplayParam ],
                         "-maxData_graph.jpg",
                         sep="" )

errorsFilename <- paste( args[ save_directory ],
                         "CHO_Errors_",
                         args[ branch_name ],
                         "_",
                         args[ maxDataToDisplayParam ],
                         "-maxData_graph.jpg",
                         sep="" )

# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# -------------------------------------------------------
# Verifying all required columns are present.
# -------------------------------------------------------

# ------------------
# Verifying 'Events'
# ------------------

print( "Verifying all required columns are present for 'events'." )

requiredColumns <- c( "Link.Down",
                      "Link.Up",
                      "Device.Down",
                      "Device.Up",
                      "Add.Host.Intent",
                      "Delete.Host.Intent",
                      "Add.Point.Intent",
                      "Delete.Point.Intent",
                      "ONOS.Down",
                      "ONOS.Up" )

tryCatch( eventsCombined <- c( event_fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from 'events'. Please check that the data and file are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( event_fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# --------------------
# Verifying 'Failures'
# --------------------

print( "Verifying all required columns are present for 'failures'." )

requiredColumns <- c( "Intent.Check.Failure",
                      "Flow.Check.Failure",
                      "Traffic.Check.Failure",
                      "Topo.Check.Failure",
                      "ONOS.Check.Failure" )

tryCatch( failureCombined <- c( failure_fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from 'failures'. Please check that the data and file are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( failure_fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# ------------------
# Verifying 'Errors'
# ------------------

print( "Verifying all required columns are present for 'errors'." )

requiredColumns <- c( "Test.Warnings",
                      "ONOS.Warnings",
                      "ONOS.Errors",
                      "Exceptions" )

tryCatch( errorCombined <- c( error_fileData[ requiredColumns] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from 'errors'. Please check that the data and file are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( error_fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# -------------------------------
# Create Events Data Frame
# -------------------------------

maxDataToDisplay <- strtoi( args[ maxDataToDisplayParam ] )

# -------------------
# 'Events' Data Frame
# -------------------

print( "Constructing data frame for 'events'." )

events_dataFrame <- melt( eventsCombined )

# Rename column names in events_dataFrame
colnames( events_dataFrame ) <- c( "Events",
                            "Type" )

# Format data frame so that the data is in the same order as it appeared in the file.
events_dataFrame$Type <- as.character( events_dataFrame$Type )
events_dataFrame$Type <- factor( events_dataFrame$Type, levels = unique( events_dataFrame$Type ) )

events_dataFrame$timeStamps <- rev( gsub('^(.{11})(.*)$', '\\1\n\\2', event_fileData$Time ) )

# Adding a temporary reversed iterative list to the events_dataFrame so that there are no gaps in-between build numbers.
events_dataFrame$iterative <- rev( seq( 1, nrow( event_fileData ), by = 1 ) )

# Omit any data that doesn't exist
events_dataFrame <- na.omit( events_dataFrame )


dataLength <- nrow( event_fileData )
moduloFactor <- floor( dataLength / limitToDisplayIndividually ) + 1

if ( dataLength > maxDataToDisplay ){
    events_dataFrame <- events_dataFrame[ events_dataFrame$iterative >= dataLength - maxDataToDisplay, ]
}

if ( moduloFactor > 1 ){
    events_dataFrame[ events_dataFrame$iterative %% moduloFactor != dataLength %% moduloFactor, ]$timeStamps <- ""
}

print( "'Events' Data Frame Results:" )
print( events_dataFrame )

# ---------------------
# 'Failures' Data Frame
# ---------------------

print( "Constructing data frame for 'failures'." )

failures_dataFrame <- melt( failureCombined )

# Rename column names in failures_dataFrame
colnames( failures_dataFrame ) <- c( "Failures",
                                     "Type" )

# Format data frame so that the data is in the same order as it appeared in the file.
failures_dataFrame$Type <- as.character( failures_dataFrame$Type )
failures_dataFrame$Type <- factor( failures_dataFrame$Type, levels = unique( failures_dataFrame$Type ) )

failures_dataFrame$timeStamps <- rev( gsub('^(.{11})(.*)$', '\\1\n\\2', failure_fileData$Time ) )

# Adding a temporary reversed iterative list to the failures_dataFrame so that there are no gaps in-between build numbers.
failures_dataFrame$iterative <- rev( seq( 1, nrow( failure_fileData ), by = 1 ) )

# Omit any data that doesn't exist
failures_dataFrame <- na.omit( failures_dataFrame )

if ( dataLength > maxDataToDisplay ){
    failures_dataFrame <- failures_dataFrame[ failures_dataFrame$iterative >= dataLength - maxDataToDisplay, ]
}

if ( moduloFactor > 1 ){
    failures_dataFrame[ failures_dataFrame$iterative %% moduloFactor != dataLength %% moduloFactor, ]$timeStamps <- ""
}

print( "'Failures' Data Frame Results:" )
print( failures_dataFrame )

# -------------------
# 'Errors' Data Frame
# -------------------

print( "Constructing data frame for 'errors'." )

errors_dataFrame <- melt( errorCombined )

# Rename column names in errors_dataFrame
colnames( errors_dataFrame ) <- c( "Errors",
                                   "Type" )

# Format data frame so that the data is in the same order as it appeared in the file.
errors_dataFrame$Type <- as.character( errors_dataFrame$Type )
errors_dataFrame$Type <- factor( errors_dataFrame$Type, levels = unique( errors_dataFrame$Type ) )

errors_dataFrame$timeStamps <- gsub('^(.{11})(.*)$', '\\1\n\\2', error_fileData$Time )

# Adding a temporary reversed iterative list to the errors_dataFrame so that there are no gaps in-between build numbers.
errors_dataFrame$iterative <- seq( 1, nrow( error_fileData ), by = 1 )

# Omit any data that doesn't exist
errors_dataFrame <- na.omit( errors_dataFrame )

if ( dataLength > maxDataToDisplay ){
    errors_dataFrame <- errors_dataFrame[ errors_dataFrame$iterative >= dataLength - maxDataToDisplay, ]
}

if ( moduloFactor > 1 ){
    errors_dataFrame[ errors_dataFrame$iterative %% moduloFactor != dataLength %% moduloFactor, ]$timeStamps <- ""
}

print( "'Errors' Data Frame Results:" )
print( errors_dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# -------------------
# Main Plot Generated
# -------------------

print( "Creating main plots." )

eventsPlot <- ggplot( data = events_dataFrame, aes( x = iterative,
                                                    y = Events,
                                                    color = Type ) )

failuresPlot <- ggplot( data = failures_dataFrame, aes( x = iterative,
                                                        y = Failures,
                                                        color = Type ) )

errorsPlot <- ggplot( data = errors_dataFrame, aes( x = iterative,
                                                    y = Errors,
                                                    color = Type ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data used in all 3 graphs." )

defaultTextSize()

yAxisTicksExponents <- seq( -1, floor( max( c( max( events_dataFrame$Events ), max( failures_dataFrame$Failures ), max( errors_dataFrame$Errors ) ) ) ^ 0.1 ) + 1, by=1 )
yAxisTicks <- 10 ^ yAxisTicksExponents
yAxisTicksLabels <- floor( yAxisTicks )

yScaleConfig <- scale_y_log10( breaks = yAxisTicks,
                               labels = yAxisTicksLabels )
xLabel <- xlab( "Time" )

print( "Generating line graph." )

lineGraphFormat <- geom_line( size = 0.5 )
pointFormat <- geom_point( size = 0 )

graphTheme <- graphTheme() + theme( axis.text.x = element_text( angle = 90, hjust = 1.0, vjust = 0.5, size = 11 ),
                                    axis.text.y = element_text( size = 17 ) )

# -------------------
# 'Events' Graph Data
# -------------------

print( "Generating 'events' graph data." )

yLabel <- ylab( "Events" )

xScaleConfig <- scale_x_continuous( breaks = events_dataFrame$iterative,
                                    label = events_dataFrame$timeStamps )

lineColorsAndLabels <- scale_color_manual( values=c( webColor( "light_blue" ),
                                            webColor( "red" ),
                                            webColor( "purple" ),
                                            webColor( "yellow" ),
                                            webColor( "orange" ),
                                            webColor( "blue" ),
                                            webColor( "magenta" ),
                                            webColor( "green" ),
                                            webColor( "brown" ),
                                            webColor( "black" )
                                          ),
                                  labels = c( "Link Down",
                                              "Link Up",
                                              "Device Down",
                                              "Device Up",
                                              "Add Host Intent",
                                              "Delete Host Intent",
                                              "Add Point Intent",
                                              "Delete Point Intent",
                                              "ONOS Down",
                                              "ONOS Up" )
                                )

title <- labs( title = eventsTitle, subtitle = lastUpdatedLabel() )

result <- eventsPlot +
          xScaleConfig +
          yScaleConfig +
          xLabel +
          yLabel +
          graphTheme +
          title +
          lineGraphFormat +
          lineColorsAndLabels +
          pointFormat

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( eventsFilename ) # from saveGraph.R

# ---------------------
# 'Failures' Graph Data
# ---------------------

print( "Generating 'failures' graph data." )

yLabel <- ylab( "Failures" )

xScaleConfig <- scale_x_continuous( breaks = failures_dataFrame$iterative,
                                    label = failures_dataFrame$timeStamps )

lineColorsAndLabels <- scale_color_manual( values=c( webColor( "red" ),
                                            webColor( "yellow" ),
                                            webColor( "green" ),
                                            webColor( "blue" ),
                                            webColor( "magenta" )
                                          ),
                                  labels = c( "Intent Check Failure",
                                              "Flow Check Failure",
                                              "Traffic Check Failure",
                                              "Topo Check Failure",
                                              "ONOS Check Failure" )
                                )

title <- labs( title = failedChecksTitle, subtitle = lastUpdatedLabel() )

result <- failuresPlot +
          xScaleConfig +
          yScaleConfig +
          xLabel +
          yLabel +
          graphTheme +
          title +
          lineGraphFormat +
          lineColorsAndLabels + wrapLegend(byrow=FALSE) +
          pointFormat


# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( failedChecksFilename ) # from saveGraph.R

# ---------------------
# 'Errors' Graph Data
# ---------------------

print( "Generating 'errors' graph data." )

yLabel <- ylab( "Errors" )

xScaleConfig <- scale_x_continuous( breaks = errors_dataFrame$iterative,
                                    label = errors_dataFrame$timeStamps )

lineColorsAndLabels <- scale_color_manual( values=c( webColor( "magenta" ),
                                            webColor( "yellow" ),
                                            webColor( "orange" ),
                                            webColor( "red" )
                                          ),
                                  labels = c( "Test Warnings",
                                              "ONOS Warnings",
                                              "ONOS Errors",
                                              "Exceptions" )
                                )

title <- labs( title = errorsTitle, subtitle = lastUpdatedLabel() )

result <- errorsPlot +
          xScaleConfig +
          yScaleConfig +
          xLabel +
          yLabel +
          graphTheme +
          title +
          lineGraphFormat +
          lineColorsAndLabels +
          pointFormat

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( errorsFilename ) # from saveGraph.R
