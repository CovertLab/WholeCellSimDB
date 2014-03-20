#!/usr/bin/perl
#
#Author: Jonathan Karr, jkarr@stanford.edu
#Affiliation: Covert Lab, Department of Bioengineering, Stanford University
#Last updated: 3/19/2014

use Cwd;
use HTML::Template;
use strict;

#options
my $organism = $ARGV[0];
my $batch_name = $ARGV[1];
my $sim_dir = $ARGV[2];
my $batch_index = $ARGV[3] + 0.;

my $storageServer = 'covertlab';
my $nodeTmpDir = '/state/partition1';
my $pathToRunTime = '/usr/local/bin/MATLAB/MATLAB_Compiler_Runtime/v81';

my $cmd = sprintf('python2.7 "%s/wcdbcli/convert_mat_to_hdf5.py"', getcwd);
my $expand_sparse_mat = 'expand_sparse_mat';

#submit jobs for each simulation
my $template = HTML::Template->new(filename => 'wcdbcli/convert_mat_to_hdf5.sh.tmpl');
$template->param(storageServer => $storageServer);
$template->param(nodeTmpDir => $nodeTmpDir);
$template->param(pathToRunTime => $pathToRunTime);
$template->param(cmd => $cmd);
$template->param(expand_sparse_mat => sprintf('%s/wcdbcli/%s', getcwd, $expand_sparse_mat));
$template->param(organism => $organism);
$template->param(batch_name => $batch_name);
$template->param(sim_dir => $sim_dir);
$template->param(batch_index => $batch_index);
   
my $jobFileName = sprintf("%s/convert_mat_to_hdf5.sh", $sim_dir);
open(FH, '>', $jobFileName) or die $!;
print FH $template->output;
close (FH);
`chmod 775 $jobFileName`;

`qsub $jobFileName`;