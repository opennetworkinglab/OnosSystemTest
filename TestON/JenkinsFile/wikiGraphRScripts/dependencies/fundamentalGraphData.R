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

graphTheme <- function(){
    theme( plot.title = element_text( hjust = 0.5, size = 32, face ='bold' ),
           axis.text.x = element_text( angle = 0, size = 14 ),
           legend.position = "bottom",
           legend.text = element_text( size = 22 ),
           legend.title = element_blank(),
           legend.key.size = unit( 1.5, 'lines' ),
           legend.direction = 'horizontal',
           plot.subtitle = element_text( size=16, hjust=1.0 ) )
}

webColor <- function( color ){
    switch( color,
            red = "#FF0000",
            redv2 = "#FF6666", # more readable version of red
            green = "#33CC33",
            blue = "#0033FF",
            light_blue = "#3399FF",
            black = "#111111",
            yellow = "#CCCC00",
            purple = "#9900FF",
            gray = "#CCCCCC",
            darkerGray = "#666666",
            orange = "#FF9900",
            magenta = "#FF00FF",
            brown = "#993300"
    )
}

wrapLegend <- function( byrow=TRUE ){
    guides( color = guide_legend( nrow = 2, byrow = byrow ) )
}

lastUpdatedLabel <- function( latestBuildDate ){
    paste( "Last Updated: ", format( latestBuildDate, "%b %d, %Y at %I:%M %p %Z" ), sep="" )
}

defaultTextSize <- function(){
    theme_set( theme_grey( base_size = 26 ) )   # set the default text size of the graph.
}
