function [ cart_point ] = to_cartesian( point )
    cart_point = [point(1); point(2)]/point(3)';
end