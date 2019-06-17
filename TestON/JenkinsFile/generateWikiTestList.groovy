#!groovy
// Copyright 2019 Open Networking Foundation (ONF)
//
// Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
// the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
// or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
//
//     TestON is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 2 of the License, or
//     (at your option) any later version.
//
//     TestON is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with TestON.  If not, see <http://www.gnu.org/licenses/>.

// This script generates the test list on the wiki.
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )

wikiContents = ""
testHTMLtableContents = ""
runningNode = "TestStation-BMs"
supportBranch1 = null
supportBranch2 = null

testCategoryContents = [:]

main()

def main(){
    test_list.init()

    supportBranch1 = test_list.convertBranchCodeToBranch( "onos-1.x" )
    supportBranch2 = test_list.convertBranchCodeToBranch( "onos-2.x" )

    initHtmlForWiki()
    initTestCategoryContents()
    wikiContents += contentsToHTML()
    wikiContents += endTable()
    wikiContents += addBranchDescription()

    debugPrintHTML()

    node ( runningNode ) {
        publishToConfluence( "Automated Test Schedule", wikiContents )
    }
}

// Initial part of the wiki page.
def initHtmlForWiki(){
    wikiContents = '''
    <table class="wrapped confluenceTable">
        <colgroup>
              <col />
              <col />
              <col />
              <col />
              <col />
              <col />
        </colgroup>
        <tbody>
            <tr>
                <th colspan="1" class="confluenceTh">
                    <br />
                </th>
                <th class="confluenceTh"><p>Monday</p></th>
                <th class="confluenceTh"><p>Tuesday</p></th>
                <th class="confluenceTh"><p>Wednesday</p></th>
                <th class="confluenceTh"><p>Thursday</p></th>
                <th class="confluenceTh"><p>Friday</p></th>
                <th class="confluenceTh"><p>Saturday</p></th>
                <th class="confluenceTh"><p>Sunday</p></th>
            </tr>'''
}

def initTestCategoryContents(){
    allCategories = test_list.getAllTestCategories()

    for ( category in allCategories ){
        testsFromCategory = test_list.getTestsFromCategory( category )

        dayOfWeekDict = [ "mon" : null,
                          "tue" : null,
                          "wed" : null,
                          "thu" : null,
                          "fri" : null,
                          "sat" : null,
                          "sun" : null ]

        for ( day in dayOfWeekDict.keySet() ){
            testsFromDay = test_list.getTestsFromDay( day, testsFromCategory )
            dayOfWeekDict[ day ] = testsFromDay
        }

        testCategoryContents.put( category, dayOfWeekDict )
    }
}

def contentsToHTML(){
    testHTMLtableContents = ""
    for ( category in testCategoryContents.keySet() ){
        categoryTableCells = ""
        categoryTableCells += '''
            <tr>
                <th colspan="1" class="confluenceTh">''' + category + '''</th>'''
        for ( day in testCategoryContents[ category ].keySet() ){
            categoryTableCells += '''
                <td class="confluenceTd">
                    <ul>'''
            for ( test in testCategoryContents[ category ][ day ].keySet() ){
                testName = test
                categoryTableCells += '''
                        <li>''' + test + addAsterisks( category, day, test ) + '''</li>'''
            }
            categoryTableCells += '''
                    </ul>
                </td>'''
        }
        categoryTableCells += '''
            </tr>'''

        testHTMLtableContents += categoryTableCells
    }
    return testHTMLtableContents
}

// adds asterisks based on the support branch number (hack)
// Example: if support branch is onos-1.x, then adds 1 asterisks, if onos-2.x, then adds 2 asterisks
def addAsterisks( category, day, test ){
    asterisks = ""
    tempDict = [ test : testCategoryContents[ category ][ day ][ test ] ]
    testBranches = test_list.getBranchesFromDay( day, tempDict )
    asteriskCount = 0

    for ( branch in testBranches ){
        if ( branch.substring( 0, 1 ) != "m" ){
            asteriskCount += branch.substring( 0, 1 ) as Integer
        }
    }

    for ( i = 0; i < asteriskCount; i++ ){
        asterisks += '''*'''
    }
    return asterisks
}

def endTable(){
    return '''
        </tbody>
    </table>'''
}

def debugPrintHTML(){
    echo "wikiContents:\n" + wikiContents
}

def addBranchDescription(){
    branchDescription = ""

    branchDescription += '''
    <p>* test runs on the <b>''' + supportBranch1 + '''</b> branch.</p>
    <p>** test runs on the <b>''' + supportBranch2 + '''</b> branch.</p>
    <p>Otherwise, test runs on the <b>''' + '''master''' + '''</b> branch.</p>'''


    return branchDescription
}

def publishToConfluence( pageName, contents ){
    // publish HTML script to wiki confluence

    publishConfluence siteName: 'wiki.onosproject.org', pageName: pageName, spaceName: 'ONOS',
                      attachArchivedArtifacts: true, buildIfUnstable: true,
                      editorList: [ confluenceWritePage( confluenceText( contents ) ) ]

}
