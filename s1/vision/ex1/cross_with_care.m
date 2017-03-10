function [ extrema ] = cross_with_care( line )
    top_row = 1;
    bottom_row = 400;
    left_col = 1;
    right_col = 264;
    tl_corner = [top_row,	left_col,	1]';
    tr_corner = [top_row,  right_col,    1]';
    br_corner = [bottom_row,	right_col,	1]';
    bl_corner = [bottom_row,   left_col,	1]';
    left_border =	cross(tl_corner, bl_corner); % 1, 0, 0: 1x+0y+0=0: x=0
    top_border =	cross(tl_corner, tr_corner); % 0, 1, 0: y=0
    right_border =	cross(tr_corner, br_corner); % 0, 1, lastCol
    bottom_border =	cross(bl_corner, br_corner); % 1, 0, lastRow

%     left_border =	[1, 0, 0];
%     top_border =	[0, 1, 0];
%     right_border =	[0, 1, right_col];
%     bottom_border =	[1, 0, bottom_row];

    left_intersection = to_cartesian(cross(line, left_border)');
    top_intersection = to_cartesian(cross(line, top_border)');
    right_intersection = to_cartesian(cross(line, right_border)');
    bottom_intersection = to_cartesian(cross(line, bottom_border)');
    idx = 1;
    extrema = zeros(2);
    if(is_valid(left_intersection))
        extrema(idx,:) = left_intersection';
        idx = idx + 1;
    end
    if(is_valid(top_intersection))
        extrema(idx,:) = top_intersection';
        idx = idx + 1;
    end
    if(is_valid(right_intersection))
        extrema(idx,:) = right_intersection';
        idx = idx + 1;
    end
    if(is_valid(bottom_intersection))
        extrema(idx,:) = bottom_intersection';
        idx = idx + 1;
    end
end