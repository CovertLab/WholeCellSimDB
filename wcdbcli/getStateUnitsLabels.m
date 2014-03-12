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

% options
units_labels.lengthSec.units = 's';
units_labels.media.units = 'various';
if ~isempty(sim.media)
    units_labels.media.labels = {{}, {'Metabolite index', 'Compartment index', 'Value', 'Initial time', 'Final time', 'Object/compartment index'}};
end
units_labels.stepSizeSec.units = 's';
units_labels.stimulus.units = 'various';
if ~isempty(sim.stimulus)
    units_labels.stimulus.labels = {{}, {'Stimulus index', 'Compartment index', 'Value', 'Initial time', 'Final time', 'Object/compartment index'}};
end

units_labels.processes.ChromosomeCondensation.stepSizeSec.units = 's';
units_labels.processes.ChromosomeSegregation.stepSizeSec.units = 's';
units_labels.processes.Cytokinesis.stepSizeSec.units = 's';
units_labels.processes.DNADamage.stepSizeSec.units = 's';
units_labels.processes.DNARepair.stepSizeSec.units = 's';
units_labels.processes.DNASupercoiling.stepSizeSec.units = 's';
units_labels.processes.FtsZPolymerization.stepSizeSec.units = 's';
units_labels.processes.HostInteraction.stepSizeSec.units = 's';
units_labels.processes.MacromolecularComplexation.stepSizeSec.units = 's';
units_labels.processes.Metabolism.stepSizeSec.units = 's';
units_labels.processes.ProteinActivation.stepSizeSec.units = 's';
units_labels.processes.ProteinDecay.stepSizeSec.units = 's';
units_labels.processes.ProteinFolding.stepSizeSec.units = 's';
units_labels.processes.ProteinModification.stepSizeSec.units = 's';
units_labels.processes.ProteinProcessingI.stepSizeSec.units = 's';
units_labels.processes.ProteinProcessingII.stepSizeSec.units = 's';
units_labels.processes.ProteinTranslocation.stepSizeSec.units = 's';
units_labels.processes.Replication.stepSizeSec.units = 's';
units_labels.processes.ReplicationInitiation.stepSizeSec.units = 's';
units_labels.processes.RibosomeAssembly.stepSizeSec.units = 's';
units_labels.processes.RNADecay.stepSizeSec.units = 's';
units_labels.processes.RNAModification.stepSizeSec.units = 's';
units_labels.processes.RNAProcessing.stepSizeSec.units = 's';
units_labels.processes.TerminalOrganelleAssembly.stepSizeSec.units = 's';
units_labels.processes.Transcription.stepSizeSec.units = 's';
units_labels.processes.TranscriptionalRegulation.stepSizeSec.units = 's';
units_labels.processes.Translation.stepSizeSec.units = 's';
units_labels.processes.tRNAAminoacylation.stepSizeSec.units = 's';

units_labels.processes.Metabolism.tolerance.units = 'fraction';
units_labels.processes.Metabolism.realmax.units = 'dimensionless';
 
% parameters
units_labels.states.Chromosome.equilibriumSuperhelicalDensity.units = 'dimensionless';
units_labels.states.Chromosome.relaxedBasesPerTurn.units = 'links/nt';
units_labels.states.Chromosome.supercoiledSuperhelicalDensityTolerance.units = 'dimensionless';

units_labels.states.FtsZRing.numFtsZSubunitsPerFilament.units = 'subunits/filament';
units_labels.states.FtsZRing.numFtsZSubunitsPerNm.units = 'subunits/nm';

units_labels.states.Geometry.density.units = 'g/L';

units_labels.states.Mass.cellInitialDryWeight.units = 'g';
units_labels.states.Mass.dryWeightFractionCarbohydrate.units = 'fraction';
units_labels.states.Mass.dryWeightFractionDNA.units = 'fraction';
units_labels.states.Mass.dryWeightFractionIon.units = 'fraction';
units_labels.states.Mass.dryWeightFractionLipid.units = 'fraction';
units_labels.states.Mass.dryWeightFractionPolyamine.units = 'fraction';
units_labels.states.Mass.dryWeightFractionProtein.units = 'fraction';
units_labels.states.Mass.dryWeightFractionRNA.units = 'fraction';
units_labels.states.Mass.dryWeightFractionVitamin.units = 'fraction';
units_labels.states.Mass.fractionWetWeight.units = 'fraction';
units_labels.states.Mass.initialBiomassConcentration.units = 'g/L';
units_labels.states.Mass.initialFractionAAsInMonomers.units = 'fraction';
units_labels.states.Mass.initialFractionNTPsInRNAs.units = 'fraction';
units_labels.states.Mass.timeAveragedCellWeight.units = 'dimensionless';
units_labels.states.Mass.dryWeightFractionNucleotide.units = 'fraction';
units_labels.states.Mass.cellInitialMassVariation.units = 'dimensionless';

units_labels.states.MetabolicReaction.initialGrowthFilterWidth.units = 'dimensionless';
units_labels.states.MetabolicReaction.meanInitialGrowthRate.units = 'cells/s';

units_labels.states.Metabolite.meanNTPConcentration.units = 'mM';
units_labels.states.Metabolite.meanNDPConcentration.units = 'mM';
units_labels.states.Metabolite.meanNMPConcentration.units = 'mM';

units_labels.states.ProteinComplex.minimumAverageExpression.units = 'molecules';

units_labels.states.ProteinMonomer.minimumAverageExpression.units = 'molecules';
units_labels.states.ProteinMonomer.macromoleculeStateInitializationVariation.units = 'dimensionless';

units_labels.states.Rna.geneExpressionRobustness.units = 'dimensionless';
units_labels.states.Rna.weightFractionMRNA.units = 'fraction';
units_labels.states.Rna.weightFractionRRNA16S.units = 'fraction';
units_labels.states.Rna.weightFractionRRNA23S.units = 'fraction';
units_labels.states.Rna.weightFractionRRNA5S.units = 'fraction';
units_labels.states.Rna.weightFractionSRNA.units = 'fraction';
units_labels.states.Rna.weightFractionTRNA.units = 'fraction';
units_labels.states.Rna.minTRnaCnt.units = 'molecules';

units_labels.states.RNAPolymerase.stateExpectations.units = '%';
units_labels.states.RNAPolymerase.stateExpectations.labels = {{'actively transcribing' 'promoter bound' 'non-specifically bound' 'free'} {}};

units_labels.states.Time.cellCycleLength.units = 's';
units_labels.states.Time.cytokinesisDuration.units = 's';
units_labels.states.Time.replicationDuration.units = 's';
units_labels.states.Time.replicationInitiationDuration.units = 's';

units_labels.processes.ChromosomeCondensation.smcSepNt.units = 'nt';
units_labels.processes.ChromosomeCondensation.smcSepProbCenter.units = 'nt';

units_labels.processes.ChromosomeSegregation.gtpCost.units = 'molecules';

units_labels.processes.Cytokinesis.rateFilamentBindingMembrane.units = '1/s';
units_labels.processes.Cytokinesis.rateFilamentDissociation.units = '1/s';
units_labels.processes.Cytokinesis.rateFtsZGtpHydrolysis.units = '1/s';

units_labels.processes.DNARepair.HR_PolA_ResectionLength.units = 'nt';
units_labels.processes.DNARepair.HR_RecA_Spacing.units = 'nt';
units_labels.processes.DNARepair.HR_RecU_CleavagePosition.units = 'nt';
units_labels.processes.DNARepair.HR_RuvAB_JunctionMigrationHop.units = 'nt';
units_labels.processes.DNARepair.NER_PcrA_StepSize.units = 'nt';
units_labels.processes.DNARepair.NER_UvrABC_IncisionMargin3.units = 'nt';
units_labels.processes.DNARepair.NER_UvrABC_IncisionMargin5.units = 'nt';
units_labels.processes.DNARepair.RM_EcoD_MethylationPosition.units = 'nt';
units_labels.processes.DNARepair.RM_EcoD_RestrictionPosition.units = 'nt';
units_labels.processes.DNARepair.RM_MunI_MethylationPosition.units = 'nt';
units_labels.processes.DNARepair.RM_MunI_RestrictionPosition.units = 'nt';

units_labels.processes.DNASupercoiling.foldChangeIntercepts.units = 'dimensionless';
units_labels.processes.DNASupercoiling.foldChangeLowerSigmaLimit.units = 'dimensionless';
units_labels.processes.DNASupercoiling.foldChangeSlopes.units = 'dimensionless';
units_labels.processes.DNASupercoiling.foldChangeUpperSigmaLimit.units = 'dimensionless';
units_labels.processes.DNASupercoiling.gyraseActivityRate.units = '1/s';
units_labels.processes.DNASupercoiling.gyraseATPCost.units = 'molecules';
units_labels.processes.DNASupercoiling.gyraseDeltaLK.units = 'links';
units_labels.processes.DNASupercoiling.gyraseMeanDwellTime.units = 's';
units_labels.processes.DNASupercoiling.gyraseSigmaLimit.units = 'dimensionless';
units_labels.processes.DNASupercoiling.topoIActivityRate.units = '1/s';
units_labels.processes.DNASupercoiling.topoIATPCost.units = 'molecules';
units_labels.processes.DNASupercoiling.topoIDeltaLK.units = 'links';
units_labels.processes.DNASupercoiling.topoISigmaLimit.units = 'dimensionless';
units_labels.processes.DNASupercoiling.topoIVActivityRate.units = '1/s';
units_labels.processes.DNASupercoiling.topoIVATPCost.units = 'molecules';
units_labels.processes.DNASupercoiling.topoIVDeltaLK.units = 'links';
units_labels.processes.DNASupercoiling.topoIVSigmaLimit.units = 'dimensionless';
units_labels.processes.DNASupercoiling.topoILogisiticConst.units = 'dimensionless';
units_labels.processes.DNASupercoiling.gyrLogisiticConst.units = 'dimensionless';

units_labels.processes.FtsZPolymerization.activationFwd.units = '1/s';
units_labels.processes.FtsZPolymerization.activationRev.units = '1/s';
units_labels.processes.FtsZPolymerization.elongationFwd.units = '1/(M*s)';
units_labels.processes.FtsZPolymerization.elongationRev.units = '1/s';
units_labels.processes.FtsZPolymerization.exchangeFwd.units = '1/(M*s)';
units_labels.processes.FtsZPolymerization.exchangeRev.units = '1/(M*s)';
units_labels.processes.FtsZPolymerization.nucleationFwd.units = '1/(M*s)';
units_labels.processes.FtsZPolymerization.nucleationRev.units = '1/s';

units_labels.processes.Metabolism.growthAssociatedMaintenance.units = 'mmol ATP/gDCW';
units_labels.processes.Metabolism.nonGrowthAssociatedMaintenance.units = 'mmol ATP/gDCW';
units_labels.processes.Metabolism.exchangeRateUpperBound_carbon.units = 'mmol/gDCW/h';
units_labels.processes.Metabolism.exchangeRateUpperBound_noncarbon.units = 'mmol/gDCW/h';
units_labels.processes.Metabolism.macromoleculeStateInitializationGrowthFactor.units = 'dimensionless';

units_labels.processes.ProteinDecay.ftsHProteaseEnergyCost.units = 'ATP/cleavage';
units_labels.processes.ProteinDecay.ftsHProteaseFragmentLength.units = 'aa';
units_labels.processes.ProteinDecay.ftsHProteaseSpecificRate.units = '1/s';
units_labels.processes.ProteinDecay.lonProteaseEnergyCost.units = 'ATP/cleavage';
units_labels.processes.ProteinDecay.lonProteaseFragmentLength.units = 'aa';
units_labels.processes.ProteinDecay.lonProteaseSpecificRate.units = '1/s';
units_labels.processes.ProteinDecay.oligoendopeptidaseFSpecificRate.units = '1/s';
units_labels.processes.ProteinDecay.proteinMisfoldingRate.units = '1/s';

units_labels.processes.ProteinProcessingI.deformylaseSpecificRate.units = '1/s';
units_labels.processes.ProteinProcessingI.methionineAminoPeptidaseSpecificRate.units = '1/s';

units_labels.processes.ProteinProcessingII.lipoproteinDiacylglycerylTransferaseSpecificRate.units = '1/s';
units_labels.processes.ProteinProcessingII.lipoproteinSignalPeptidaseSpecificRate.units = '1/s';

units_labels.processes.ProteinTranslocation.preproteinTranslocase_aaTranslocatedPerATP.units = 'aa/ATP';
units_labels.processes.ProteinTranslocation.SRP_GTPUsedPerMonomer.units = 'GTP/monomer';
units_labels.processes.ProteinTranslocation.translocaseSpecificRate.units = 'aa/s';

units_labels.processes.Replication.dnaPolymeraseElongationRate.units = 'nt/s';
units_labels.processes.Replication.laggingBackupClampReloadingLength.units = 'nt';
units_labels.processes.Replication.ligaseRate.units = '1/s';
units_labels.processes.Replication.okazakiFragmentMeanLength.units = 'nt';
units_labels.processes.Replication.primerLength.units = 'nt';
units_labels.processes.Replication.ssbComplexSpacing.units = 'nt';
units_labels.processes.Replication.startingOkazakiLoopLength.units = 'nt';
units_labels.processes.Replication.rnaPolymeraseCollisionMeanDwellTime.units = 's';
units_labels.processes.Replication.ssbDissociationRate.units = '1/s';

units_labels.processes.ReplicationInitiation.k_inact.units = '1/g';
units_labels.processes.ReplicationInitiation.k_Regen.units = '1/h';
units_labels.processes.ReplicationInitiation.K_Regen_P4.units = 'g/L';
units_labels.processes.ReplicationInitiation.kb1ADP.units = '1/(nM*h)';
units_labels.processes.ReplicationInitiation.kb1ATP.units = '1/(nM*h)';
units_labels.processes.ReplicationInitiation.kb2ADP.units = '1/(nM*h)';
units_labels.processes.ReplicationInitiation.kb2ATP.units = '1/(nM*h)';
units_labels.processes.ReplicationInitiation.kd1ADP.units = '1/h';
units_labels.processes.ReplicationInitiation.kd1ATP.units = '1/h';
units_labels.processes.ReplicationInitiation.siteCooperativity.units = 'dimensionless';
units_labels.processes.ReplicationInitiation.stateCooperativity.units = 'dimensionless';

units_labels.processes.RNADecay.peptidylTRNAHydrolaseSpecificRate.units = '1/s';
units_labels.processes.RNADecay.ribonucleaseRFragmentLength.units = 'nt';

units_labels.processes.RNAProcessing.enzymeEnergyCost_DeaD.units = 'ATP/cleavage';
units_labels.processes.RNAProcessing.enzymeEnergyCost_RsgA.units = 'GTP/cleavage';
units_labels.processes.RNAProcessing.enzymeSpecificRate_DeaD.units = '1/s';
units_labels.processes.RNAProcessing.enzymeSpecificRate_RNAseIII.units = '1/s';
units_labels.processes.RNAProcessing.enzymeSpecificRate_RNAseJ.units = '1/s';
units_labels.processes.RNAProcessing.enzymeSpecificRate_RNAseP.units = '1/s';
units_labels.processes.RNAProcessing.enzymeSpecificRate_RsgA.units = '1/s';

units_labels.processes.Transcription.rnaPolymeraseElongationRate.units = 'nt/s';

units_labels.processes.Translation.ribosomeElongationRate.units = 'aa/s';
units_labels.processes.Translation.tmRNABindingProbability.units = 'dimensionless';

% time courses
s = sim.state('Chromosome');
colLabels = {'chromosome-1, (+)-strand', 'chromosome-1, (-)-strand', 'chromosome-2, (+)-strand', 'chromosome-2, (-)-strand'};
units_labels.states.Chromosome.polymerizedRegions.units = 'nt';
units_labels.states.Chromosome.polymerizedRegions.labels = {{} colLabels};
units_labels.states.Chromosome.linkingNumbers.units = 'links';
units_labels.states.Chromosome.linkingNumbers.labels = {{} colLabels};
units_labels.states.Chromosome.monomerBoundSites.units = 'protein monomer index';
units_labels.states.Chromosome.monomerBoundSites.labels = {{} colLabels};
units_labels.states.Chromosome.complexBoundSites.units = 'protein complex index';
units_labels.states.Chromosome.complexBoundSites.labels = {{} colLabels};
units_labels.states.Chromosome.gapSites.units = 'dimensionless';
units_labels.states.Chromosome.gapSites.labels = {{} colLabels};
units_labels.states.Chromosome.abasicSites.units = 'dimensionless';
units_labels.states.Chromosome.abasicSites.labels = {{} colLabels};
units_labels.states.Chromosome.damagedSugarPhosphates.units = 'metabolite index';
units_labels.states.Chromosome.damagedSugarPhosphates.labels = {{} colLabels};
units_labels.states.Chromosome.damagedBases.units = 'metabolite index';
units_labels.states.Chromosome.damagedBases.labels = {{} colLabels};
units_labels.states.Chromosome.intrastrandCrossLinks.units = 'dimensionless';
units_labels.states.Chromosome.intrastrandCrossLinks.labels = {{} colLabels};
units_labels.states.Chromosome.strandBreaks.units = 'dimensionless';
units_labels.states.Chromosome.strandBreaks.labels = {{} colLabels};
units_labels.states.Chromosome.hollidayJunctions.units = 'dimensionless';
units_labels.states.Chromosome.hollidayJunctions.labels = {{} colLabels};
units_labels.states.Chromosome.segregated.units = 'dimensionless';
units_labels.states.Chromosome.singleStrandedRegions.units = 'nt';
units_labels.states.Chromosome.singleStrandedRegions.labels = {{} colLabels};
units_labels.states.Chromosome.doubleStrandedRegions.units = 'nt';
units_labels.states.Chromosome.doubleStrandedRegions.labels = {{} colLabels};
units_labels.states.Chromosome.geneCopyNumbers.units = 'molecules';
units_labels.states.Chromosome.geneCopyNumbers.labels = {s.gene.wholeCellModelIDs' {}};
units_labels.states.Chromosome.transcriptionUnitCopyNumbers.units = 'molecules';
units_labels.states.Chromosome.transcriptionUnitCopyNumbers.labels = {s.transcriptionUnitWholeCellModelIDs' {}};
units_labels.states.Chromosome.ploidy.units = 'molecules';
units_labels.states.Chromosome.superhelicalDensity.units = 'dimensionless';
units_labels.states.Chromosome.superhelicalDensity.labels = {{} colLabels};

units_labels.states.FtsZRing.numEdgesOneStraight.units = 'molecules';
units_labels.states.FtsZRing.numEdgesTwoStraight.units = 'molecules';
units_labels.states.FtsZRing.numEdgesTwoBent.units = 'molecules';
units_labels.states.FtsZRing.numResidualBent.units = 'molecules';
units_labels.states.FtsZRing.numEdges.units = 'dimensionless';

units_labels.states.Geometry.width.units = 'm';
units_labels.states.Geometry.pinchedDiameter.units = 'm';
units_labels.states.Geometry.volume.units = 'L';
units_labels.states.Geometry.cylindricalLength.units = 'm';
units_labels.states.Geometry.surfaceArea.units = 'm^2';
units_labels.states.Geometry.totalLength.units = 'm';
units_labels.states.Geometry.pinchedCircumference.units = 'm';
units_labels.states.Geometry.pinched.units = 'dimensionless';
units_labels.states.Geometry.chamberVolume.units = 'L';

s = sim.state('Host');
units_labels.states.Host.isBacteriumAdherent.units = 'dimensionless';
units_labels.states.Host.isTLRActivated.units = 'dimensionless';
units_labels.states.Host.isTLRActivated.labels = {s.tlrIDs' {}};
units_labels.states.Host.isNFkBActivated.units = 'dimensionless';
units_labels.states.Host.isInflammatoryResponseActivated.units = 'dimensionless';

s = sim.state('Mass');
for i = 1:numel(s.dependentStateNames)
    units_labels.states.Mass.(s.dependentStateNames{i}).units = 'g';
    units_labels.states.Mass.(s.dependentStateNames{i}).labels = {{} s.compartment.wholeCellModelIDs'};
end

s = sim.state('MetabolicReaction');
units_labels.states.MetabolicReaction.growth.units = 'cells/s';
units_labels.states.MetabolicReaction.fluxs.units = 'rxn/s';
units_labels.states.MetabolicReaction.fluxs.labels = {s.reactionWholeCellModelIDs' {}};
units_labels.states.MetabolicReaction.doublingTime.units = 's';

s = sim.state('Metabolite');
tiledLabels = cellfun(@(x,y) sprintf('%s[%s]', x, y), s.wholeCellModelIDs(:, ones(size(s.compartment.wholeCellModelIDs))), s.compartment.wholeCellModelIDs(:, ones(size(s.wholeCellModelIDs)))', 'UniformOutput', false);
tiledLabels = reshape(tiledLabels, [], 1);
units_labels.states.Metabolite.counts.units = 'molecules';
units_labels.states.Metabolite.counts.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'};
units_labels.states.Metabolite.processRequirements.units = 'molecules';
units_labels.states.Metabolite.processRequirements.labels = {tiledLabels' sim.processWholeCellModelIDs'};
units_labels.states.Metabolite.processAllocations.units = 'molecules';
units_labels.states.Metabolite.processAllocations.labels = {tiledLabels' sim.processWholeCellModelIDs'};
units_labels.states.Metabolite.processUsages.units = 'molecules';
units_labels.states.Metabolite.processUsages.labels = {tiledLabels' sim.processWholeCellModelIDs'};

units_labels.states.Polypeptide.boundMRNAs.units = 'protein coding gene index';
units_labels.states.Polypeptide.nascentMonomerLengths.units = 'aa';
units_labels.states.Polypeptide.proteolysisTagLengths.units = 'aa';

s = sim.state('ProteinComplex');
row_labels = s.wholeCellModelIDs;
row_labels(s.nascentIndexs)     = cellfun(@(x) sprintf('%s-%s', x, 'nascent'),     row_labels(s.nascentIndexs),     'UniformOutput', false);
row_labels(s.matureIndexs)      = cellfun(@(x) sprintf('%s-%s', x, 'mature'),      row_labels(s.matureIndexs),      'UniformOutput', false);
row_labels(s.inactivatedIndexs) = cellfun(@(x) sprintf('%s-%s', x, 'inactivated'), row_labels(s.inactivatedIndexs), 'UniformOutput', false);
row_labels(s.boundIndexs)       = cellfun(@(x) sprintf('%s-%s', x, 'bound'),       row_labels(s.boundIndexs),       'UniformOutput', false);
row_labels(s.misfoldedIndexs)   = cellfun(@(x) sprintf('%s-%s', x, 'misfolded'),   row_labels(s.misfoldedIndexs),   'UniformOutput', false);
row_labels(s.damagedIndexs)     = cellfun(@(x) sprintf('%s-%s', x, 'damaged'),     row_labels(s.damagedIndexs),     'UniformOutput', false);
units_labels.states.ProteinComplex.counts.units = 'molecules';
units_labels.states.ProteinComplex.counts.labels = {row_labels' s.compartment.wholeCellModelIDs'};

s = sim.state('ProteinMonomer');
row_labels = s.wholeCellModelIDs;
row_labels(s.nascentIndexs)        = cellfun(@(x) sprintf('%s-%s', x, 'nascent'),         row_labels(s.nascentIndexs),        'UniformOutput', false);
row_labels(s.processedIIndexs)     = cellfun(@(x) sprintf('%s-%s', x, 'processed-I'),     row_labels(s.processedIIndexs),     'UniformOutput', false);
row_labels(s.processedIIIndexs)    = cellfun(@(x) sprintf('%s-%s', x, 'processed-II'),    row_labels(s.processedIIIndexs),    'UniformOutput', false);
row_labels(s.signalSequenceIndexs) = cellfun(@(x) sprintf('%s-%s', x, 'signal-sequence'), row_labels(s.signalSequenceIndexs), 'UniformOutput', false);
row_labels(s.foldedIndexs)         = cellfun(@(x) sprintf('%s-%s', x, 'folded'),          row_labels(s.foldedIndexs),         'UniformOutput', false);
row_labels(s.matureIndexs)         = cellfun(@(x) sprintf('%s-%s', x, 'mature'),          row_labels(s.matureIndexs),         'UniformOutput', false);
row_labels(s.inactivatedIndexs)    = cellfun(@(x) sprintf('%s-%s', x, 'inactivated'),     row_labels(s.inactivatedIndexs),    'UniformOutput', false);
row_labels(s.boundIndexs)          = cellfun(@(x) sprintf('%s-%s', x, 'bound'),           row_labels(s.boundIndexs),          'UniformOutput', false);
row_labels(s.misfoldedIndexs)      = cellfun(@(x) sprintf('%s-%s', x, 'misfolded'),       row_labels(s.misfoldedIndexs),      'UniformOutput', false);
row_labels(s.damagedIndexs)        = cellfun(@(x) sprintf('%s-%s', x, 'damaged'),         row_labels(s.damagedIndexs),        'UniformOutput', false);
units_labels.states.ProteinMonomer.counts.units = 'molecules';
units_labels.states.ProteinMonomer.counts.labels = {row_labels' s.compartment.wholeCellModelIDs'};

units_labels.states.Ribosome.states.units = 'state index (-1=>stalled, 0=>not exist, 1=>actively translating)'; 
units_labels.states.Ribosome.boundMRNAs.units = 'protein coding gene index';
units_labels.states.Ribosome.mRNAPositions.units = 'nt';
units_labels.states.Ribosome.tmRNAPositions.units = 'nt';
units_labels.states.Ribosome.stateOccupancies.units = '%';
units_labels.states.Ribosome.stateOccupancies.labels = {{'actively translating', 'not exist', 'stalled'} {}};
units_labels.states.Ribosome.nActive.units = 'molecules';
units_labels.states.Ribosome.nNotExist.units = 'molecules';
units_labels.states.Ribosome.nStalled.units = 'molecules';

s = sim.state('Rna');
row_labels = s.wholeCellModelIDs;
row_labels(s.nascentIndexs)       = cellfun(@(x) sprintf('%s-%s', x, 'nascent'),        row_labels(s.nascentIndexs),       'UniformOutput', false);
row_labels(s.processedIndexs)     = cellfun(@(x) sprintf('%s-%s', x, 'processed'),      row_labels(s.processedIndexs),     'UniformOutput', false);
row_labels(s.intergenicIndexs)    = cellfun(@(x) sprintf('%s-%s', x, 'intergenic'),     row_labels(s.intergenicIndexs),    'UniformOutput', false);
row_labels(s.matureIndexs)        = cellfun(@(x) sprintf('%s-%s', x, 'mature'),         row_labels(s.matureIndexs),        'UniformOutput', false);
row_labels(s.boundIndexs)         = cellfun(@(x) sprintf('%s-%s', x, 'bound'),          row_labels(s.boundIndexs),         'UniformOutput', false);
row_labels(s.misfoldedIndexs)     = cellfun(@(x) sprintf('%s-%s', x, 'misfolded'),      row_labels(s.misfoldedIndexs),     'UniformOutput', false);
row_labels(s.damagedIndexs)       = cellfun(@(x) sprintf('%s-%s', x, 'damaged'),        row_labels(s.damagedIndexs),       'UniformOutput', false);
row_labels(s.aminoacylatedIndexs) = cellfun(@(x) sprintf('%s-%s', x, 'aminmoacylated'), row_labels(s.aminoacylatedIndexs), 'UniformOutput', false);
units_labels.states.Rna.counts.units = 'molecules';
units_labels.states.Rna.counts.labels = {row_labels' s.compartment.wholeCellModelIDs'};

s = sim.state('Rna');
units_labels.states.RNAPolymerase.states.units = 'state index (-3=>promoter bound, -2=>free, -1=>non-specifically bound, 0=>not exist, 1=>actively transcribing)';
units_labels.states.RNAPolymerase.positionStrands.units = 'nt';
units_labels.states.RNAPolymerase.transcriptionFactorBindingProbFoldChange.units = 'dimensionless';
units_labels.states.RNAPolymerase.transcriptionFactorBindingProbFoldChange.labels = {s.wholeCellModelIDs(s.nascentIndexs)' {'chromosome-1', 'chromosome-2'}};
units_labels.states.RNAPolymerase.supercoilingBindingProbFoldChange.units = 'dimensionless';
units_labels.states.RNAPolymerase.supercoilingBindingProbFoldChange.labels = {s.wholeCellModelIDs(s.nascentIndexs)' {'chromosome-1', 'chromosome-2'}};
units_labels.states.RNAPolymerase.stateOccupancies.units = '%';
units_labels.states.RNAPolymerase.stateOccupancies.labels = {{'actively transcribing' 'promoter bound' 'non-specifically bound' 'free'} {}};
units_labels.states.RNAPolymerase.nActive.units = 'molecules';
units_labels.states.RNAPolymerase.nSpecificallyBound.units = 'molecules';
units_labels.states.RNAPolymerase.nNonSpecificallyBound.units = 'molecules';
units_labels.states.RNAPolymerase.nFree.units = 'molecules';

s = sim.state('Stimulus');
units_labels.states.Stimulus.values.units = 'various';
units_labels.states.Stimulus.values.labels = {s.wholeCellModelIDs' s.compartment.wholeCellModelIDs'};

units_labels.states.Time.values.units = 's';

units_labels.states.Transcript.boundTranscriptionUnits.units = 'transcription unit index';
units_labels.states.Transcript.boundTranscriptProgress.units = 'nt';
units_labels.states.Transcript.boundTranscriptChromosome.units = 'chromosome index';
units_labels.states.Transcript.rnaBoundRNAPolymerases.units = 'molecules';

%% verify label dimensions
propNames = setdiff(fieldnames(units_labels), {'processes', 'states'});
for i = 1:numel(propNames)
    if isfield(units_labels.(propNames{i}), 'labels')
        labels = units_labels.(propNames{i}).labels;
        assertEqual([1 2], size(labels));
        assertTrue(1 >= size(labels{1}, 1))
        assertTrue(1 >= size(labels{2}, 1))
        
        if size(labels{1}, 2) >= 1
            assertEqual(size(sim.(propNames{i}), 1), size(labels{1}, 2))
        end
        if size(labels{2}, 2) >= 1
            assertEqual(size(sim.(propNames{i}), 2), size(labels{2}, 2))
        end
    end
end

processNames = fieldnames(units_labels.processes);
for i = 1:numel(processNames)
    propNames = fieldnames(units_labels.processes.(processNames{i}));
    for j = 1:numel(propNames)
        if isfield(units_labels.processes.(processNames{i}).(propNames{j}), 'labels')
            labels = units_labels.processes.(processNames{i}).(propNames{j}).labels;
            assertEqual([1 2], size(labels));
            assertTrue(1 >= size(labels{1}, 1))
            assertTrue(1 >= size(labels{2}, 1))
            
            if size(labels{1}, 2) >= 1
                assertEqual(size(sim.process(processNames{i}).(propNames{j}), 1), size(labels{1}, 2))
            end
            if size(labels{2}, 2) >= 1
                assertEqual(size(sim.process(processNames{i}).(propNames{j}), 2), size(labels{2}, 2))
            end
        end
    end
end

stateNames = fieldnames(units_labels.states);
for i = 1:numel(stateNames)
    propNames = fieldnames(units_labels.states.(stateNames{i}));
    for j = 1:numel(propNames)
        if isfield(units_labels.states.(stateNames{i}).(propNames{j}), 'labels')
            labels = units_labels.states.(stateNames{i}).(propNames{j}).labels;
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