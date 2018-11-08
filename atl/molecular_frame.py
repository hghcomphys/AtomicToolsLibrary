
class MolecularFrame(object):
    """
    This class manipulates lammps input format in form of a molecular frame.
    
    Example
    
        water = MolecularFrame()
        water.read_lmp('lammps.lmp')
        print  water
        water.shift_atoms_id(1000)
        water.write_lmp('out.lmp')


    Not implemented yet:
    *** comments
    *** tilted unit cell
    """
    
    # atoms, angles, bonds, dihedrals
    # n_atoms, n_angles, n_bonds, n_dihedrals
    # move, center
    # read (lmp,xyz,pdb)
    # set,get (charge,mass,aid,mid)
    # keep_block, keep_cylinder
    # del_block, del_cylinder
    # replace_mol, replace_atom   
    # replicate, recenter
    
    # Box:       [[Lx],[Ly],[Lz]]
    # Masses:    [atype,mass]
    # Atoms:     [aid,mid,atype,charge,xpos,ypos,zpos,imx,imy,imz,type]
    # Bonds:     [bid,btype,aid,aid]
    # Angles:    [anid,antype,aid,aid,aid]
    # Dihedrals: [did,dtype,aid,aid,aid,aid]
    # Impropers: [did,dtype,aid,aid,aid,aid]
    
     
    def __init__(self, attributes='Box Masses Atoms Bonds Angles Dihedrals Impropers Types', molframe={}):
        
        import copy
        self._attributes = attributes    
        self._molframe = copy.deepcopy( molframe )
        
          
    def __str__(self):
        out='Molecular Frame\n---------------\n'
        for k in self._molframe.keys():
            out = out + '%d '%len(self._molframe[k]) + k + '\n'
        return out
    
        
    def __clean_molframe(self):
        for k in self._attributes.split():
            self._molframe[k] = []   
            
            
    @property
    def n_atoms(self):     
        return len(self._molframe['Atoms'])
    
    @property
    def n_bonds(self):     
        return len(self._molframe['Bonds'])
    
    @property
    def n_angles(self):     
        return len(self._molframe['Angles'])
       
    @property
    def n_dihedrals(self):     
        return len(self._molframe['Dihedrals'])
    
    @property
    def n_impropers(self):     
        return len(self._molframe['Impropers']) 
    
    @property
    def lx(self):     
        return (self._molframe['Box'][0][1] - self._molframe['Box'][0][0])
    
    @property
    def ly(self):     
        return (self._molframe['Box'][1][1] - self._molframe['Box'][1][0])
    
    @property
    def lz(self):     
        return (self._molframe['Box'][2][1] - self._molframe['Box'][2][0])
    
    @property
    def box(self):     
        return self.lx, self.ly, self.lz
    
    @property
    def atom_types(self):     
        return self._molframe['Types'][0]

    @property
    def bond_types(self):
        return self._molframe['Types'][1]

    @property
    def angle_types(self):
        return self._molframe['Types'][2]

    @property
    def dihedral_types(self):
        return self._molframe['Types'][3]

    @property
    def improper_types(self):
        return self._molframe['Types'][3]
      
                      
    # read/write .xyz format
    # -----------------------------------
    def read_xyz(self, filename, frame=-1): 
        
        self.__clean_molframe()
        
        import atl.io as io #!!!
        data = io.read_xyz(filename, frame)  
        
        aid=1; mid=1
        for d in data:           
            #      [aid, mid, atype, charge, xpos, ypos, zpos, imx, imy, imz, type]
            atom = [aid, mid, 0    , 0.0   , d[1], d[2], d[3], 0  , 0  , 0  , d[0] ]
            self._molframe['Atoms'].append( atom )
            aid += 1
            mid += 1
   

    def write_xyz(self, filename):             
        with open(filename, 'w') as fo:
            fo.write('%d\nGenerated by ATL\n'%self.n_atoms)
            for at in self._molframe['Atoms']:           
                fo.write('%s %f %f %f\n'%(at[10],at[4],at[5],at[6]))
    
    
    # read/write lammps format
    # -----------------------------------
    def read_lmp(self,filename):
        self.__clean_molframe()
        from lammps_input import read_lammps_input
        data=read_lammps_input(filename, self._attributes)
        for k in data.keys():
            self._molframe[k] = data[k]
    
    
    def write_lmp(self, filename):
        from lammps_input import write_lammps_input
        write_lammps_input(filename, self._molframe)
        
    
    # Merging two molecules
    # -----------------------------------
    def __add__(self, other):
        
        # first step just merging two molecules without common atomic types
        # then function that merges two atomic types
        # mass values are usful to identify atomic types

        molframe = {}     
        for attribute in self._attributes.split():
            
            if attribute == 'Boxes':
                molframe[attribute] = self._molframe[attribute] # taking boxsize from first object

            elif attribute == 'Types':
                molframe[attribute] = [ x+y for x,y in zip(self._molframe[attribute], other._molframe[attribute]) ]

            else:
                tmp_list = [self._molframe[attribute], other._molframe[attribute]]
                molframe[attribute] = reduce(lambda x,y: x+y, tmp_list)
            
        return MolecularFrame(attributes=self._attributes,molframe=molframe) 
           
    
    # Shifting ids
    # ------------------------------------------------
    def __shift_id(self, attribute, columns, shift_id):
        for mf in self._molframe[attribute]:
            for i in range(columns[0], columns[1]):
                mf[i] += shift_id
                
   
    def shift_atoms_id(self, shift_id=0):        
        self.__shift_id('Atoms',     [0,1], shift_id)
        self.__shift_id('Bonds',     [2,4], shift_id)
        self.__shift_id('Angles',    [2,5], shift_id)
        self.__shift_id('Dihedrals', [2,6], shift_id)
        self.__shift_id('Impropers', [2,6], shift_id)
                
    
    def shift_bonds_id(self, shift_id=0):
        self.__shift_id('Bonds', [0,1], shift_id)
    
    
    def shift_angles_id(self, shift_id=0):
        self.__shift_id('Angles', [0,1], shift_id)
            
    
    def shift_dihedrals_id(self, shift_id=0):
        self.__shift_id('Dihedrals', [0,1], shift_id)
    

    def shift_impropers_id(self, shift_id=0):
        self.__shift_id('Impropers', [0,1], shift_id)
        
        
    def shift_mols_id(self, shift_id=0):
        self.__shift_id('Atoms', [1,2], shift_id)
    
           
    def shift_atom_types(self, shift_id=0):
        self.__shift_id('Atoms',  [2,3], shift_id)
        self.__shift_id('Masses', [0,1], shift_id)
    
    
    def shift_bond_types(self, shift_id=0):
        self.__shift_id('Bonds', [1,2], shift_id)
    
    
    def shift_angle_types(self, shift_id=0):
        self.__shift_id('Angles', [1,2], shift_id)
    
    
    def shift_dihedral_types(self, shift_id=0):
        self.__shift_id('Dihedrals', [1,2], shift_id)
    
    
    def shift_improper_types(self, shift_id=0):
        self.__shift_id('Impropers', [1,2], shift_id)
        
    
    # Setting properties
    # ------------------------------------------------
    
    
    # Moving Atoms
    # ------------------------------------------------
    def move_atoms(self, move=[0.,0.,0.], box=False):
        # Atoms
        for atom in self._molframe['Atoms']:
            for i in range(3):
                atom[i+4] += move[i] # xpos,ypos,zpos
        # Box
        if box:
            for i in range(3):
                for j in range(2):
                    self._molframe['Box'][i][j] += move[i]


    # Water tip3p (adding bonds and angles)
    # ------------------------------------------------
    def apply_tip3p(self, O_type, mol_id=0):
        """
        This function adds to molecular frame bond and angle information of identified water molecules
        that is determined by a input argument. Importantly, It assumes that each water oxygen in atomic section
        is followed by two hydrogen atoms. It increases the number of bond and angle types by one.

        Example:

            mf = MolecularFrame()
            mf.read_lmp('../grn-wt-h9.3.lmp') # without water bonds & angles
            mf.apply_tip3p(O_type=3,mol_id=1) # adding bonds and angles
            mf.write_lmp('../out.lmp')
        """

        mid = mol_id
        self._molframe['Types'][1] += 1 # ading bond type
        self._molframe['Types'][2] += 1 # ading angle type

        for n in range(self.n_atoms):

            if self._molframe['Atoms'][n][2] != O_type: continue;  # only water oxygen

            # Atoms
            mid+=1
            for i in range(3):
                self._molframe['Atoms'][n+i][1] = mid

            # Bonds
            for i in range(2):
                self._molframe['Bonds'].append([self.n_bonds+1, self.bond_types,
                                                self._molframe['Atoms'][n][0],
                                                self._molframe['Atoms'][n+i+1][0]])
            # Angles
            self._molframe['Angles'].append([self.n_angles+1, self.angle_types,
                                             self._molframe['Atoms'][n+1][0],
                                             self._molframe['Atoms'][n][0],
                                             self._molframe['Atoms'][n+2][0]])
