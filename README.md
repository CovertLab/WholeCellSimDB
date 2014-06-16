# WholeCellSimDB v1.1.0

<a name="table_of_contents"/>

1. [About](#about)
2. [User's guide: browsing and searching simulations](#users)
3. [Developer's guide: Installing your own WholeCellSimDB server and storing simulations](#developers)
4. [Need help?](#help)
5. [Implementation](#implementation)
6. [Development team](#team)
7. [Citing WholeCellSimDB](#citing)
8. [License](#license)


<a name="about"/>
## About
WholeCellSimDB is a database of whole-cell model simulations designed to make it easy for researchers to explore and analyze whole-cell model predictions including predicted:
* Metabolite concentrations,
* DNA, RNA and protein expression,
* DNA-bound protein positions,
* DNA modification positions, and
* Ribome positions.

See [wholecell.stanford.edu](http://wholecell.stanford.edu) for additional information about whole-cell models.

<a name="users"/>
## User's guide: browsing and searching simulations
See the online [user's guide](http://www.wholecellsimdb.org/help).

<a name="developers"/>
## Developer's guide: Installing your own WholeCellSimDB server and storing simulations
See the online [developers's guide](http://www.wholecellsimdb.org/help) for installation instructions including a list of required packages and instructions for integreating WholeCellSimDB with whole-cell models.

<a name="help"/>
## Need help?
Please contact the development team at [wholecell@lists.stanford.edu](mailto:wholecell@lists.stanford.edu).

<a name="implementation"/>
## Implementation
WholeCellSimDB is a hybrid SQL/HDF database implemented in [Python](http://www.python.org/). The [Django](https://www.djangoproject.com/) framework was used to construct a [MySQL](http://www.mysql.org) database containing simulation metadata as well as links to HDF files containing the simulation predictions. The [H5py](http://www.h5py.org/) package was used to read and write HDF files. Full text search over the simulation metadata was implemented using [Xapian](http://xapian.org/) and [Haystack](http://haystacksearch.org/). The web interface was run using [Apache](http://httpd.apache.org/) and [mod_wsgi](https://code.google.com/p/modwsgi/). The web interface was developed using [flot](http://www.flotcharts.org/), [Google Fonts](https://www.google.com/fonts), [jQuery](http://jquery.com/), [jqTree](http://mbraak.github.io/jqTree), [jQWidgets](http://www.jqwidgets.com/), and [FamFamFam Silk icons](http://www.famfamfam.com/lab/icons/silk/).

<a name="team"/>
## Development team
WholeCellSimDB was developed by researchers at Mount Sinai School of Medicine, Stanford University, and the University of Prince Edward Island.
* [Jonathan Karr](http://research.mssm.edu/karr), Mount Sinai School of Medicine
* [Nolan Phillips](http://ca.linkedin.com/pub/nolan-phillips/68/935/702), University of Prince Edward Island
* [Markus Covert](http://covertlab.stanford.edu), Stanford University

<a name="citing"/>
## Citing WholeCellSimDB
Please see the following for more information or to cite WholeCellSimDB:
* Karr JR et al. WholeCellSimDB: hybrid HDF/SQL database for whole-cell model predictions. (In preparation).
* Karr JR, Sanghvi JC, Macklin DN, Gutschow MV, Jacobs JM, Bolival B, Assad-Garcia N, Glass JI, Covert MW. A Whole-Cell Computational Model Predicts Phenotype from Genotype. *Cell* **150**, 389-401 (2012). [Cell](http://www.cell.com/abstract/S0092-8674(12)00776-3) | [PubMed](http://www.ncbi.nlm.nih.gov/pubmed/22817898)

<a name="license"/>
## The MIT License (MIT)

Copyright &copy; 2013-2014 Covert Lab, Stanford University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
