%% options
options = sim.getOptions();
fprintf('%% options\n');

option_names = setdiff(fieldnames(options), {'states', 'processes'});
for i = 1:numel(option_names)
    fprintf('units_labels.%s.units = '''';\n', option_names{i});
    fprintf('units_labels.%s.value = [];\n', option_names{i});
end
if ~isempty(option_names)
    fprintf('\n');
end

state_names = fieldnames(options.states);
for i = 1:numel(state_names)
    option_names = fieldnames(options.states.(state_names{i}));
    for j = 1:numel(option_names)
        fprintf('units_labels.states.%s.%s.units = '''';\n', state_names{i}, option_names{j});
        fprintf('units_labels.states.%s.%s.value = [];\n', state_names{i}, option_names{j});
    end
    if ~isempty(option_names)
        fprintf('\n');
    end
end

process_names = fieldnames(options.processes);
for i = 1:numel(process_names)
    option_names = fieldnames(options.processes.(process_names{i}));
    for j = 1:numel(option_names)
        fprintf('units_labels.processes.%s.%s.units = '''';\n', process_names{i}, option_names{j});
        fprintf('units_labels.processes.%s.%s.value = [];\n', process_names{i}, option_names{j});
    end
    if ~isempty(option_names)
        fprintf('\n');
    end
end

%% parameters
parameters = sim.getParameters();
fprintf('%% parameters\n');

parameter_names = setdiff(fieldnames(parameters), {'states', 'processes'});
for i = 1:numel(parameter_names)
    fprintf('units_labels.%s.units = '''';\n', parameter_names{i});
    fprintf('units_labels.%s.value = [];\n', parameter_names{i});
end
if ~isempty(parameter_names)
    fprintf('\n');
end

state_names = fieldnames(parameters.states);
for i = 1:numel(state_names)
    parameter_names = fieldnames(parameters.states.(state_names{i}));
    for j = 1:numel(parameter_names)
        fprintf('units_labels.states.%s.%s.units = '''';\n', state_names{i}, parameter_names{j});
        fprintf('units_labels.states.%s.%s.value = [];\n', state_names{i}, parameter_names{j});
    end
    if ~isempty(parameter_names)
        fprintf('\n');
    end
end

process_names = fieldnames(parameters.processes);
for i = 1:numel(process_names)
    parameter_names = fieldnames(parameters.processes.(process_names{i}));
    for j = 1:numel(parameter_names)
        fprintf('units_labels.processes.%s.%s.units = '''';\n', process_names{i}, parameter_names{j});
        fprintf('units_labels.processes.%s.%s.value = [];\n', process_names{i}, parameter_names{j});        
    end
    if ~isempty(parameter_names)
        fprintf('\n');
    end
end

%% time courses
 for i = 1:numel(sim.states), 
    s = sim.states{i}; 
    for j = 1:numel(s.stateNames)
        fprintf('units_labels.%s.%s.units=''%s'';\n', s.wholeCellModelID(7:end), s.stateNames{j}, '');
        fprintf('units_labels.%s.%s.labels=[];\n', s.wholeCellModelID(7:end), s.stateNames{j});
    end
    for j = 1:numel(s.dependentStateNames)
        fprintf('units_labels.%s.%s.units=''%s'';\n', s.wholeCellModelID(7:end), s.dependentStateNames{j}, '');
        fprintf('units_labels.%s.%s.labels=[];\n', s.wholeCellModelID(7:end), s.dependentStateNames{j});
    end
    fprintf('\n')
end