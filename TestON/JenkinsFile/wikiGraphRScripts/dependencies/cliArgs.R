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

database_host <- 1
database_host_str <- "<database-host>"

database_port <- 2
database_port_str <- "<database-port>"

database_u_id <- 3
database_u_id_str <- "<database-user-id>"

database_pw <- 4
database_pw_str <- "<database-password>"

graph_title <- 5
graph_title_str <- "<graph-title>"

branch_name <- 6
branch_name_str <- "<branch-name>"

save_directory_str <- "<directory-to-save-graph>"

usage <- function( filename, specialArgsList = c() ){
    special_args_str = ""
    for ( a in specialArgsList) {
        special_args_str = paste( special_args_str, "<", a, "> ", sep="" )
    }
    output <- paste( "Usage: Rscript",
                     filename,
                     database_host_str,
                     database_port_str,
                     database_u_id_str,
                     database_pw_str,
                     graph_title_str,
                     branch_name_str,
                     special_args_str,
                     sep=" " )
    output <- paste( output, save_directory_str, sep="" )
    print( output )
}