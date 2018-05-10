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
has_flow_obj = 1
database_host = 2
database_port = 3
database_u_id = 4
database_pw = 5
test_name = 6
branch_name = 7
batch_size = 8
old_flow = 9
save_directory = 10

# Command line arguments are read.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )    # For databases

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( is.na( args[ save_directory ] ) ){

    print( paste( "Usage: Rscript SCPFIntentInstallWithdrawRerouteLat.R",
                                  "<isFlowObj>" ,
                                  "<database-host>",
                                  "<database-port>",
                                  "<database-user-id>",
                                  "<database-password>",
                                  "<test-name>",
                                  "<branch-name>",
                                  "<batch-size>",
                                  "<using-old-flow>",
                                  "<directory-to-save-graphs>",
                                  sep=" " ) )
    quit( status = 1 )  # basically exit(), but in R
}

# -----------------------------------
# Create File Name and Title of Graph
# -----------------------------------

print( "Creating filename and title of graph." )

chartTitle <- "Intent Install, Withdraw, & Reroute Latencies"
flowObjFileModifier <- ""
errBarOutputFile <- paste( args[ save_directory ],
                    "SCPFIntentInstallWithdrawRerouteLat_",
                    args[ branch_name ],
                    sep="" )

if ( args[ has_flow_obj ] == "y" ){
    errBarOutputFile <- paste( errBarOutputFile, "_fobj", sep="" )
    flowObjFileModifier <- "fobj_"
    chartTitle <- paste( chartTitle, "w/ FlowObj" )
}
if ( args[ old_flow ] == "y" ){
    errBarOutputFile <- paste( errBarOutputFile, "_OldFlow", sep="" )
    chartTitle <- paste( chartTitle,
                         "With Eventually Consistent Flow Rule Store",
                         sep="\n" )
}
errBarOutputFile <- paste( errBarOutputFile,
                           "_",
                           args[ batch_size ],
                           "-batchSize_graph.jpg",
                           sep="" )

chartTitle <- paste( chartTitle,
                     "\nBatch Size =",
                     args[ batch_size ],
                     sep=" " )

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

# ---------------------------------------
# Intent Install and Withdraw SQL Command
# ---------------------------------------
print( "Generating Intent Install and Withdraw SQL Command" )

installWithdrawSQLCommand <- paste( "SELECT * FROM intent_latency_",
                                    flowObjFileModifier,
                                    "tests WHERE batch_size=",
                                    args[ batch_size ],
                                    " AND branch = '",
                                    args[ branch_name ],
                                    "' AND date IN ( SELECT MAX( date ) FROM intent_latency_",
                                    flowObjFileModifier,
                                    "tests WHERE branch='",
                                    args[ branch_name ],
                                    "' AND ",
                                    ( if( args[ old_flow ] == 'y' ) "" else "NOT " ) ,
                                    "is_old_flow",
                                    ")",
                                    sep="" )

print( "Sending Intent Install and Withdraw SQL command:" )
print( installWithdrawSQLCommand )
installWithdrawData <- dbGetQuery( con, installWithdrawSQLCommand )

# --------------------------
# Intent Reroute SQL Command
# --------------------------

print( "Generating Intent Reroute SQL Command" )

rerouteSQLCommand <- paste( "SELECT * FROM intent_reroute_latency_",
                            flowObjFileModifier,
                            "tests WHERE batch_size=",
                            args[ batch_size ],
                            " AND branch = '",
                            args[ branch_name ],
                            "' AND date IN ( SELECT MAX( date ) FROM intent_reroute_latency_",
                            flowObjFileModifier,
                            "tests WHERE branch='",
                            args[ branch_name ],
                            "' AND ",
                            ( if( args[ old_flow ] == 'y' ) "" else "NOT " ) ,
                            "is_old_flow",
                            ")",
                            sep="" )

print( "Sending Intent Reroute SQL command:" )
print( rerouteSQLCommand )
rerouteData <- dbGetQuery( con, rerouteSQLCommand )

# **********************************************************
# STEP 2: Organize Data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

# -------------------------------------------------------
# Combining Install, Withdraw, and Reroute Latencies Data
# -------------------------------------------------------

print( "Combining Install, Withdraw, and Reroute Latencies Data" )

if ( ncol( rerouteData ) == 0 ){  # Checks if rerouteData exists, so we can exclude it if necessary

    requiredColumns <- c( "install_avg",
                          "withdraw_avg"  )

    tryCatch( avgs <- c( installWithdrawData[ requiredColumns] ),
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
} else{
    colnames( rerouteData ) <- c( "date",
                                  "name",
                                  "date",
                                  "branch",
                                  "is_old_flow",
                                  "commit",
                                  "scale",
                                  "batch_size",
                                  "reroute_avg",
                                  "reroute_std" )

    tryCatch( avgs <- c( installWithdrawData[ 'install_avg' ],
                         installWithdrawData[ 'withdraw_avg' ],
                         rerouteData[ 'reroute_avg' ] ),
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

}

# Combine lists into data frames.
dataFrame <- melt( avgs )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing data frame." )

if ( ncol( rerouteData ) == 0 ){  # Checks if rerouteData exists (due to batch size) for the dataFrame this time
    dataFrame$scale <- c( installWithdrawData$scale,
                          installWithdrawData$scale )

    dataFrame$stds <- c( installWithdrawData$install_std,
                         installWithdrawData$withdraw_std )
} else{
    dataFrame$scale <- c( installWithdrawData$scale,
                          installWithdrawData$scale,
                          rerouteData$scale )

    dataFrame$stds <- c( installWithdrawData$install_std,
                         installWithdrawData$withdraw_std,
                         rerouteData$reroute_std )
}

colnames( dataFrame ) <- c( "ms",
                            "type",
                            "scale",
                            "stds" )

# Format data frame so that the data is in the same order as it appeared in the file.
dataFrame$type <- as.character( dataFrame$type )
dataFrame$type <- factor( dataFrame$type, levels=unique( dataFrame$type ) )

dataFrame <- na.omit( dataFrame ) # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graph.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# -------------------
# Main Plot Generated
# -------------------

print( "Creating the main plot." )

mainPlot <- ggplot( data = dataFrame, aes( x = scale,
                                           y = ms,
                                           ymin = ms,
                                           ymax = ms + stds,
                                           fill = type ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

theme_set( theme_grey( base_size = 22 ) )
barWidth <- 1.3
xScaleConfig <- scale_x_continuous( breaks = c( 1, 3, 5, 7, 9) )
xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )
imageWidth <- 15
imageHeight <- 10
imageDPI <- 200
errorBarColor <- rgb( 140, 140, 140, maxColorValue=255 )

theme <- theme( plot.title=element_text( hjust = 0.5, size = 32, face='bold' ),
                legend.position="bottom",
                legend.text=element_text( size=22 ),
                legend.title = element_blank(),
                legend.key.size = unit( 1.5, 'lines' ),
                plot.subtitle = element_text( size=16, hjust=1.0 ) )

subtitle <- paste( "Last Updated: ", format( Sys.time(), format = "%b %d, %Y at %I:%M %p %Z" ), sep="" )

title <- labs( title = chartTitle, subtitle = subtitle )

colors <- scale_fill_manual( values=c( "#F77670",
                                       "#619DFA",
                                       "#18BA48" ) )

# Store plot configurations as 1 variable
fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        title +
                        colors

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph with error bars." )

barGraphFormat <- geom_bar( stat = "identity",
                            width = barWidth,
                            position = "dodge" )

errorBarFormat <- geom_errorbar( width = barWidth,
                                 position = position_dodge( barWidth ),
                                 color = errorBarColor )

values <- geom_text( aes( x = dataFrame$scale,
                          y = dataFrame$ms + 0.035 * max( dataFrame$ms ),
                          label = format( dataFrame$ms,
                                          digits = 3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          position = position_dodge( width = barWidth ),
                          size = 5.5,
                          fontface = "bold" )

wrapLegend <- guides( fill = guide_legend( nrow = 1, byrow = TRUE ) )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          values +
          wrapLegend

# -----------------------
# Exporting Graph to File
# -----------------------

print( paste( "Saving bar chart with error bars to", errBarOutputFile ) )

tryCatch( ggsave( errBarOutputFile,
                  width = imageWidth,
                  height = imageHeight,
                  dpi = imageDPI ),
          error = function( e ){
              print( "[ERROR] There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
              print( e )
              quit( status = 1 )
          }
        )

print( paste( "[SUCCESS] Successfully wrote bar chart with error bars out to", errBarOutputFile ) )
quit( status = 0 )
