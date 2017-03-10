function [ valid ] = is_valid( point )
    valid = point(1) < 401 & point(1) > 0 & point(2) < 265 & point(2) > 0;
end