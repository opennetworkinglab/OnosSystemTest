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

imageWidth <- 15
imageHeight <- 10
imageDPI <- 200

saveGraph <- function( outputFile ){
    print( paste( "Saving result graph to", outputFile ) )

    tryCatch( ggsave( outputFile,
                      width = imageWidth,
                      height = imageHeight,
                      dpi = imageDPI ),
              error = function( e ){
                  print( "[ERROR]: There was a problem saving the graph due to a graph formatting exception.  Error dump:" )
                  print( e )
                  quit( status = 1 )
              }
            )

    print( paste( "[SUCCESS]: Successfully wrote result graph out to", outputFile ) )
}