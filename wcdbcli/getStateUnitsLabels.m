%getStateUnitsLabels
% Returns struct containing state units and labels
%
% Author: Jonathan Karr, jkarr@stanford.edu
% Affilitation: Covert Lab, Department of Bioengineering, Stanford University
% Last updated: 3/9/2014
function units_labels = getStateUnitsLabels()
%% import classes
import edu.stanford.covert.cell.sim.util.CachedSimulationObjectUtil;

%% get label data
sim = CachedSimulationObjectUtil.load();

%% collect units, labels
units_labels = struct();

s = sim.state('Chromosome');
colLabels = {'chrosome-1, (+)-strand', 'chromosome-1, (-)-strand', 'chrosome-2, (+)-strand', 'chromosome-2, (-)-strand'};
units_labels.Chromosome.polymerizedRegions.units = 'nt';
units_labels.Chromosome.polymerizedRegions.labels = {{} colLabels};
units_labels.Chromosome.linkingNumbers.units = 'links';
units_labels.Chromosome.linkingNumbers.labels = {{} colLabels};
units_labels.Chromosome.monomerBoundSites.units = 'protein monomer index';
units_labels.Chromosome.monomerBoundSites.labels = {{} colLabels};
units_labels.Chromosome.complexBoundSites.units = 'protein complex index';
units_labels.Chromosome.complexBoundSites.labels = {{} colLabels};
units_labels.Chromosome.gapSites.units = 'dimensionless';
units_labels.Chromosome.gapSites.labels = {{} colLabels};
units_labels.Chromosome.abasicSites.units = 'dimensionless';
units_labels.Chromosome.abasicSites.labels = {{} colLabels};
units_labels.Chromosome.damagedSugarPhosphates.units = 'metabolite index';
units_labels.Chromosome.damagedSugarPhosphates.labels = {{} colLabels};
units_labels.Chromosome.damagedBases.units = 'metabolite index';
units_labels.Chromosome.damagedBases.labels = {{} colLabels};
units_labels.Chromosome.intrastrandCrossLinks.units = 'dimensionless';
units_labels.Chromosome.intrastrandCrossLinks.labels = {{} colLabels};
units_labels.Chromosome.strandBreaks.units = 'dimensionless';
units_labels.Chromosome.strandBreaks.labels = {{} colLabels};
units_labels.Chromosome.hollidayJunctions.units = 'dimensionless';
units_labels.Chromosome.hollidayJunctions.labels = {{} colLabels};
units_labels.Chromosome.segregated.units = 'dimensionless';
units_labels.Chromosome.singleStrandedRegions.units = 'nt';
units_labels.Chromosome.singleStrandedRegions.labels = {{} colLabels};
units_labels.Chromosome.doubleStrandedRegions.units = 'nt';
units_labels.Chromosome.doubleStrandedRegions.labels = {{} colLabels};
units_labels.Chromosome.geneCopyNumbers.units = 'molecules';
units_labels.Chromosome.geneCopyNumbers.labels = {s.gene.wholeCellModelIDs' {}};
units_labels.Chromosome.transcriptionUnitCopyNumbers.units = 'molecules';
units_labels.Chromosome.transcriptionUnitCopyNumbers.labels = {s.transcriptionUnitWholeCellModelIDs' {}};
units_labels.Chromosome.ploidy.units = 'molecules';
units_labels.Chromosome.superhelicalDensity.units = 'dimensionless';
units_labels.Chromosome.superhelicalDensity.labels = {{} colLabels};

units_labels.FtsZRing.numEdgesOneStraight.units = 'molecules';
units_labels.FtsZRing.numEdgesTwoStraight.units = 'molecules';
units_labels.FtsZRing.numEdgesTwoBent.units = 'molecules';
units_labels.FtsZRing.numResidualBent.units = 'molecules';
units_labels.FtsZRing.numEdges.units = 'dimensionless';

units_labels.Geometry.width.units = 'm';
units_labels.Geometry.pinchedDiameter.units = 'm';
units_labels.Geometry.volume.units = 'L';
units_labels.Geometry.cylindricalLength.units = 'm';
units_labels.Geometry.surfaceArea.units = 'm^2';
units_labels.Geometry.totalLength.units = 'm';
units_labels.Geometry.pinchedCircumference.units = 'm';
units_labels.Geometry.pinched.units = 'dimensionless';
units_labels.Geometry.chamberVolume.units = 'L';

s = sim.state('Host');
units_labels.Host.isBacteriumAdherent.units = 'dimensionless';
units_labels.Host.isTLRActivated.units = 'dimensionless';
units_labels.Host.isTLRActivated.labels = {s.tlrIDs' {}};
units_labels.Host.isNFkBActivated.units = 'dimensionless';
units_labels.Host.isInflammatoryResponseActivated.units = 'dimensionless';

s = sim.state('Mass');
for i = 1:numel(s.dependentStateNames)
    units_labels.Mass.(s.dependentStateNames{i}).units = 'g';
    units_labels.Mass.(s.dependentStateNames{i}).labels = {{} s.compartment.wholeCellModelIDs'};
end

s = sim.state('MetabolicReaction');
units_labels.MetabolicReaction.growth.units = 'cells/s';
units_labels.MetabolicReaction.fluxs.units = 'rxn/s';
units_labels.MetabolicReaction.fluxs.labels = {s.reactionWholeCellModelIDs' {}};
units_labels.MetabolicReaction.doublingTime.units = 's';

s = sim.state('Metabolite');
tiledLabels = cellfun(@(x,y) sprintf('%s[%s]', x, y), s.wholeCellModelIDs(:, ones(size(s.compartment.wholeCellModelIDs))), s.compartment.wholeCellModelIDs(:, ones(size(s.wholeCellModelIDs)))', 'UniformOutput', false);
tiledLabels = reshape(tiledLabels, [], 1);
units_labels.Metabolite.counts.units = 'molecules';
units_labels.Metabolite.counts.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'};
units_labels.Metabolite.processRequirements.units = 'molecules';
units_labels.Metabolite.processRequirements.labels = {tiledLabels' sim.processWholeCellModelIDs'};
units_labels.Metabolite.processAllocations.units = 'molecules';
units_labels.Metabolite.processAllocations.labels = {tiledLabels' sim.processWholeCellModelIDs'};
units_labels.Metabolite.processUsages.units = 'molecules';
units_labels.Metabolite.processUsages.labels = {tiledLabels' sim.processWholeCellModelIDs'};

units_labels.Polypeptide.boundMRNAs.units = 'protein coding gene index';
units_labels.Polypeptide.nascentMonomerLengths.units = 'aa';
units_labels.Polypeptide.proteolysisTagLengths.units = 'aa';

s = sim.state('ProteinComplex');
units_labels.ProteinComplex.counts.units = 'molecules';
units_labels.ProteinComplex.counts.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'}; %TODO tiling

s = sim.state('ProteinMonomer');
units_labels.ProteinMonomer.counts.units = 'molecules';
units_labels.ProteinMonomer.counts.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'}; %TODO tiling

units_labels.Ribosome.states.units = 'state index (-1=>stalled, 0=>not exist, 1=>actively translating)'; %todo
units_labels.Ribosome.boundMRNAs.units = 'protein coding gene index';
units_labels.Ribosome.mRNAPositions.units = 'nt';
units_labels.Ribosome.tmRNAPositions.units = 'nt';
units_labels.Ribosome.stateOccupancies.units = '%';
units_labels.Ribosome.stateOccupancies.labels = {{'actively translating', 'not exist', 'stalled'} {}};
units_labels.Ribosome.nActive.units = 'molecules';
units_labels.Ribosome.nNotExist.units = 'molecules';
units_labels.Ribosome.nStalled.units = 'molecules';

s = sim.state('Rna');
units_labels.Rna.counts.units = 'molecules';
units_labels.Rna.counts.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'}; %TODO tiling

s = sim.state('Rna');
units_labels.RNAPolymerase.states.units = 'state index (-3=>promoter bound, -2=>free, -1=>non-specifically bound, 0=>not exist, 1=>actively transcribing)';
units_labels.RNAPolymerase.positionStrands.units = 'nt';
units_labels.RNAPolymerase.transcriptionFactorBindingProbFoldChange.units = 'dimensionless';
units_labels.RNAPolymerase.transcriptionFactorBindingProbFoldChange.labels = {s.wholeCellModelIDs(s.nascentIndexs)' {'chromosome-1', 'chromosome-2'}};
units_labels.RNAPolymerase.supercoilingBindingProbFoldChange.units = 'dimensionless';
units_labels.RNAPolymerase.supercoilingBindingProbFoldChange.labels = {s.wholeCellModelIDs(s.nascentIndexs)' {'chromosome-1', 'chromosome-2'}};
units_labels.RNAPolymerase.stateOccupancies.units = '%';
units_labels.RNAPolymerase.stateOccupancies.labels = {{'actively transcribing' 'promoter bound' 'non-specifically bound' 'free'} {}};
units_labels.RNAPolymerase.nActive.units = 'molecules';
units_labels.RNAPolymerase.nSpecificallyBound.units = 'molecules';
units_labels.RNAPolymerase.nNonSpecificallyBound.units = 'molecules';
units_labels.RNAPolymerase.nFree.units = 'molecules';

s = sim.state('Stimulus');
units_labels.Stimulus.values.units = 'various';
units_labels.Stimulus.values.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'};

units_labels.Time.values.units = 's';

units_labels.Transcript.boundTranscriptionUnits.units = 'transcription unit index';
units_labels.Transcript.boundTranscriptProgress.units = 'nt';
units_labels.Transcript.boundTranscriptChromosome.units = 'chromosome index';
units_labels.Transcript.rnaBoundRNAPolymerases.units = 'molecules';

%% verify label dimensions
stateNames = fieldnames(units_labels);
for i = 1:numel(stateNames)
    propNames = fieldnames(units_labels.(stateNames{i}));
    for j = 1:numel(propNames)
        if isfield(units_labels.(stateNames{i}).(propNames{j}), 'labels')
            labels = units_labels.(stateNames{i}).(propNames{j}).labels;
            assertEqual([1 2], size(labels));
            assertTrue(1 >= size(labels{1}, 1))
            assertTrue(1 >= size(labels{2}, 1))
            
            if size(labels{1}, 2) >= 1
                assertEqual(size(sim.state(stateNames{i}).(propNames{j}), 1), size(labels{1}, 2))
            end
            if size(labels{2}, 2) >= 1
                assertEqual(size(sim.state(stateNames{i}).(propNames{j}), 2), size(labels{2}, 2))
            end
        end
    end
end