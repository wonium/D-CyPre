from argparse import Namespace
import torch
import torch.nn as nn

from .mpn import MPN
from .mpn_mol import MPN_mol


class MoleculeModel(nn.Module):
    """A MoleculeModel is a model which contains a message passing network following by feed-forward layers."""

    def __init__(self):
        """
        Initializes the MoleculeModel.

        :param classification: Whether the model is a classification model.
        """
        super(MoleculeModel, self).__init__()

    def create_encoder(self, args: Namespace):
        """
        Creates the message passing encoder for the model.

        :param args: Arguments.
        """
        self.encoder = MPN(args)
        self.encoder_mol=MPN_mol(args)

    def forward(self, mols, BD_v_batch):
        """
        Runs the MoleculeModel on input.

        :param input: Input.
        :return: The output of the MoleculeModel.
        """
        atoms_v,bonds_v,t_atoms,t_bonds=self.encoder(mols, BD_v_batch)
        mol_vecs_atoms,mol_vecs_bonds=self.encoder_mol(mols, BD_v_batch)

        atoms_v = torch.concat([atoms_v,mol_vecs_atoms],dim=1)
        bonds_v = torch.concat([bonds_v,mol_vecs_bonds],dim=1)

        r_bonds = self.ffn_bonds(bonds_v)
        r_atoms = self.ffn_bonds(atoms_v)
        t_atoms=t_atoms[1:]
        t_all = torch.concat([t_bonds,t_atoms],dim=0)
        r_all = torch.concat([r_bonds,r_atoms],dim=0)
        v_all = torch.concat([bonds_v,atoms_v],dim=0)
        return r_all,t_all,v_all
