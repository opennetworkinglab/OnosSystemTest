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

pipelineMinValue = 1000

initSQL <- function( host, port, user, pass ) {
    dbConnect( dbDriver( "PostgreSQL" ),
               dbname = "onostest",
               host = host,
               port = strtoi( port ),
               user = user,
               password = pass )
}

simpleSQLCommand <- function( testName, branch, limit=0 ){
    paste( "SELECT * FROM executed_test_tests WHERE actual_test_name='",
           testName,
           "' AND branch='",
           branch,
           "' ORDER BY date DESC ",
           if (limit > 0) "LIMIT " else "",
           if (limit > 0) limit else "",
           sep="" )
}

retrieveData <- function( con, sqlCommand ){

    print( "Sending SQL command:" )
    print( sqlCommand )

    result <- dbGetQuery( con, sqlCommand )

    # Check if data has been received
    if ( nrow( result ) == 0 ){
        print( "[ERROR]: No data received from the databases. Please double check this by manually running the SQL command." )
        quit( status = 1 )
    }
    result
}

generateMultiTestMultiBuildSQLCommand <- function( branch, testsToInclude, buildsToShow ){
    tests <- getTestList( testsToInclude )
    multiTestSQLCommand( branch, tests, buildsToShow, TRUE )
}

generateMultiTestSingleBuildSQLCommand <- function( branch, testsToInclude, buildToShow ){
    tests <- getTestList( testsToInclude )
    operator <- "= "
    if ( buildToShow == "latest" ){
        operator <- ">= "
        buildToShow <- "1000"
    }

    multiTestSQLCommand( branch, tests, buildToShow, FALSE, operator )
}

generateGroupedTestSingleBuildSQLCommand <- function( branch, groupsToInclude, buildToShow ){
    operator <- "= "
    if( buildToShow == "latest" ){
        operator <- ">= "
        buildToShow <- "1000"
    }

    tests <- strsplit( groupsToInclude, ";" )

    sqlCommands <- c()

    for( i in 1:length( tests[[1]] ) ){
        splitTestList <- strsplit( tests[[1]][ i ], "-" )
        testList <- splitTestList[[1]][2]

        testsCommand <- "'"
        for ( test in as.list( strsplit( testList, "," )[[1]] ) ){
            testsCommand <- paste( testsCommand, test, "','", sep="" )
        }
        testsCommand <- substr( testsCommand, 0, nchar( testsCommand ) - 2 )

        sqlCommands = c( sqlCommands, multiTestSQLCommand( branch, testsCommand, buildToShow, FALSE, operator ) )
    }
    sqlCommands
}

getTitlesFromGroupTest <- function( branch, groupsToInclude ){
    tests <- strsplit( groupsToInclude, ";" )
    titles <- list()
    for( i in 1:length( tests[[1]] ) ){
        splitTestList <- strsplit( tests[[1]][ i ], "-" )
        titles[[i]] <- splitTestList[[1]][1]
    }
    titles
}

getTestList <- function( testsToInclude ){
    tests <- "'"
    for ( test in as.list( strsplit( testsToInclude, "," )[[1]] ) ){
        tests <- paste( tests, test, "','", sep="" )
    }
    tests <- substr( tests, 0, nchar( tests ) - 2 )
    tests
}

multiTestSQLCommand <- function( branch, tests, builds, isDisplayingMultipleBuilds, operator=">= " ){
    if ( isDisplayingMultipleBuilds ){
        operator2 <- "<="
        multipleBuildsToShow <- builds
        singleBuild <- pipelineMinValue
    }
    else{
        operator2 <- "="
        multipleBuildsToShow <- 1
        singleBuild <- builds
    }

    paste( "SELECT * ",
           "FROM executed_test_tests a ",
           "WHERE ( SELECT COUNT( * ) FROM executed_test_tests b ",
           "WHERE b.branch='",
           branch,
           "' AND b.actual_test_name IN (",
           tests,
           ") AND a.actual_test_name = b.actual_test_name AND a.date <= b.date AND b.build ", operator,
           singleBuild,
           " ) ",
           operator2,
           " ",
           multipleBuildsToShow,
           " AND a.branch='",
           branch,
           "' AND a.actual_test_name IN (",
           tests,
           ") AND a.build ", operator,
           singleBuild,
           " ORDER BY a.actual_test_name DESC, a.date DESC",
           sep="")
}
