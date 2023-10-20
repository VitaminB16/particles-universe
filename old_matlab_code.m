function output = UniverseGame(nParticles,velocity)
%inspired by Thomas Schmickl and Martin Stefanec of
%University of Graz, Austria


v = velocity;
%theta = angle;
global radius
radius = 1;
global particlePos
particlePos = rand(nParticles,3);

particlePos(:,3) = particlePos(:,3)*360;
scatter(particlePos(:,1),particlePos(:,2));
%xlim([-10,10]); ylim([-10,10]);
p = 0;
while 1 ~= 2
    p = p+1;
    particlePos(:,3) = mod(particlePos(:,3),360); %default turn
    for j = 1:nParticles
        coord = particlePos(j,1:2); direction = particlePos(j,3);
        particlePos(j,3) = mod(direction + WhereToTurn(coord,direction),360);
    end
    particlePos(:,1) = particlePos(:,1) + v*cosd(particlePos(:,3));
    particlePos(:,2) = particlePos(:,2) + v*sind(particlePos(:,3))
    scatter(particlePos(:,1),particlePos(:,2));
    hold on
    for ii = 1:nParticles
        x0 = particlePos(ii,1); y0 = particlePos(ii,2);
        direction = particlePos(ii,3);
        x1 = x0+0.02*cosd(direction);
        y1 = y0+0.02*sind(direction);
        line([x0,x1],[y0,y1]);
        text(x0+0.015,y0,num2str(WhereToTurn([x0,y0],direction)));
    end
    title(sprintf('%i',p));
    hold off
    %xlim([0.5-1 0.5+1]); ylim([0.5-1 0.5+1]);
    pause(eps);
    output = particlePos;
end

function answer = WhereToTurn(coord,direction)
    x0 = coord(1); y0 = coord(2);
    leftCounter = 0; rightCounter = 0;
    for i = 1:nParticles
        x1 = particlePos(i,1); y1 = particlePos(i,2);
        bearing = atan2d(y1-y0,x1-x0);
        bearing = mod(bearing - direction,360);
        if (pdist([x0,y0;x1,y1])<radius) && bearing<180
            leftCounter = leftCounter + 1; %count the particles to the left
        elseif (pdist([x0,y0;x1,y1])<radius) && bearing>180
            rightCounter = rightCounter + 1; %count particles to the right
        end
        
    end
    answer = sign(leftCounter-rightCounter);
    %a: turn left; -a: turn right; 0: don't turn
end
end
