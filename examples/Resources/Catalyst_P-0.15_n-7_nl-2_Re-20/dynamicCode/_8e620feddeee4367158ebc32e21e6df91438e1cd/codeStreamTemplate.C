/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Copyright (C) YEAR OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Description
    Template for use with codeStream.

\*---------------------------------------------------------------------------*/

#include "dictionary.H"
#include "Ostream.H"
#include "Pstream.H"
#include "unitConversion.H"

//{{{ begin codeInclude

//}}} end codeInclude

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

extern "C"
{
    void codeStream_8e620feddeee4367158ebc32e21e6df91438e1cd
    (
        Ostream& os,
        const dictionary& dict
    )
    {
//{{{ begin code
        #line 57 "/home/gilgonza/work/decoupledTemperature-Momentum/cases/Catalyst_P-0.15_n-7_nl-2_Re-100/system/blockMeshDict/#codeStream"
scalar nCellsR = Foam::readScalar(dict.lookup("nCellsR"));
        scalar R = Foam::readScalar(dict.lookup("Rext"));
        scalar Fiz = Foam::readScalar(dict.lookup("Fiz"));
        scalar Foz = Foam::readScalar(dict.lookup("Foz"));
        scalar nCellsLong = (int)round(nCellsR*(Foz-Fiz)/R);
        //Info << "--------------------------------------------------------- nCellsLong = " << nCellsLong << endl;
        writeEntry(os, "", nCellsLong);
//}}} end code
    }
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

