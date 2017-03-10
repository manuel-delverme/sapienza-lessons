close all;

RGB = imread('gantrycrane.png');
figure, imshow(RGB);
hold on
ù
[x, y, button] = ginput(2);
X = [x, y];
x1 = [X(1,:), 1];
x2 = [X(2,:), 1];
line = cross(x1', x2');
plot([x2(1),x1(1)],[x2(2),x1(2)],'Color','r','LineWidth',2)

extrema = cross_with_care(line);
plot([extrema(1,1), extrema(2,1)],[extrema(1,2), extrema(2,2)],'Color','b','LineWidth',3)
zextrema