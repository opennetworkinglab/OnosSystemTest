<h1>Wiki Graph Scripts</h1>

The scripts that generate the graphs are written in the R programming language.

The scripts are structured in the following format:
1. Data Management
    * Data is obtained from the databases through SQL. CLI arguments, filename, and titles are also handled here.
        1. Importing libraries
        2. Command line arguments
        3. Title of the graph
        4. Filename
        5. SQL Initialization and Data Gathering
2. Organize Data
    * Raw data is sorted into a data frame.  The data frame is used in generating the graph.
        1. Combining data into a single list.
        2. Using the list to construct a data frame
        3. Adding data as columns to the data frame
3. Generate Graphs
    * The graphs are formatted and constructed here.
        1. Main plot generated
        2. Fundamental variables assigned
        3. Generate specific graph format
        4. Exporting graph to file
