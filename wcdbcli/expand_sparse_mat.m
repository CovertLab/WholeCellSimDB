function expand_sparse_mat(in_filename, out_filename, out_filename_h5)

warning('on', 'MATLAB:save:sizeTooBigForMATFile'); 

try
    in = load(in_filename); 
    out.data = full(in.data); 
    save(out_filename, '-struct', 'out'); 
    
    [~, id] = lastwarn(); 
    if strcmp(id, 'MATLAB:save:sizeTooBigForMATFile')
        delete(out_filename); 
        save(out_filename_h5, '-struct', 'out', '-v7.3'); 
    end
end