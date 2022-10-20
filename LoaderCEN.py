# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoaderCEN
                                 A QGIS plugin
 Blablabla
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-05-11
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Romain Montillet
        email                : r.montillet@cen-na.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from .LoaderCEN_dialog import LoaderCENDialog
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from PyQt5 import *

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import processing
from pathlib import Path
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .LoaderCEN_dialog import LoaderCENDialog
import os.path
import urllib
import tempfile



class Popup(QWidget):
    def __init__(self, parent=None):
        super(Popup, self).__init__(parent)

        self.plugin_dir = os.path.dirname(__file__)

        self.text_edit = QTextBrowser()
        text = open(self.plugin_dir +'/info_changelog.html').read()
        self.text_edit.setHtml(text)
        self.text_edit.setFont(QtGui.QFont("Calibri",weight=QtGui.QFont.Bold))


        self.text_edit.setWindowTitle("Nouveautés")
        self.text_edit.setMinimumSize(500,200)
        self.text_edit.setMaximumSize(500,200)

class LoaderCEN:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LoaderCEN_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LoaderCEN')
        self.dlg = LoaderCENDialog()

        self.RelativePath = Path(__file__).parent.resolve()

        self.movie = QMovie(str(self.RelativePath) + "/loading.gif")  # récupération du gif via le chemin relatif du plugin
        self.dlg.label_3.setMovie(self.movie)
        self.dlg.label_2.setMovie(self.movie)
        self.dlg.label_10.setMovie(self.movie)

        self.movie.start()

        self.dlg.label_2.hide()
        self.dlg.label_3.hide()
        self.dlg.label_10.hide()


        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.dlg.comboBox.currentIndexChanged.connect(self.chargement_dalles_MNT)

        self.dlg.commandLinkButton.clicked.connect(self.popup)


        self.dlg.commandLinkButton_2.clicked.connect(self.chargement_dalles_orthos_20cm)

        self.dlg.commandLinkButton_3.clicked.connect(self.chargement_dalles_orthos_50cm)

        self.dlg.pushButton.clicked.connect(self.chargement_MNT_1m)

        self.dlg.pushButton_2.clicked.connect(self.orthos)

        self.dlg.pushButton_3.clicked.connect(self.chargement_cadastre)

        #dossier_dalles = 'https://sig.dsi-cen.org/qgis/downloads/dalles_mnt_1m/'
        #dalles_dept = [fname for fname in os.listdir(dossier_dalles) if fname.endswith('.geojson')]

        dalles_dept = ["Allier", "Charente", "Charente-Maritime", "Correze", "Creuse", "Dordogne", "Gironde", "Landes", "Lot-et-Garonne", "Pyrenees-Atlantique", "Deux-Sevres", "Vienne", "Haute-Vienne"]
        self.dlg.comboBox.addItems(set(dalles_dept))


        metadonnees_plugin = open(self.plugin_dir + '/metadata.txt')
        infos_metadonnees = metadonnees_plugin.readlines()

        derniere_version = urllib.request.urlopen("https://sig.dsi-cen.org/qgis/downloads/last_version_loadercen.txt")
        num_last_version = derniere_version.readlines()[0].decode("utf-8")

        # print(":"+num_last_version+":")
        # print(":"+infos_metadonnees[8]+":")
        #
        # print(type(num_last_version))
        # print(type(infos_metadonnees[8]))
        #
        # print(len(num_last_version))
        # print(len(infos_metadonnees[8]))

        version_utilisateur = infos_metadonnees[8].splitlines()

        if infos_metadonnees[8].splitlines() == num_last_version.splitlines():
            iface.messageBar().pushMessage("Plugin à jour", "Votre version de LoaderCEN %s est à jour !" %version_utilisateur, level=Qgis.Success, duration=5)
        else:
            iface.messageBar().pushMessage("Information :", "Une nouvelle version de LoaderCEN est disponible, veuillez mettre à jour le plugin !", level=Qgis.Info, duration=120)



        with tempfile.TemporaryDirectory() as self.tmpdirname:
            print('le dossier temporaire a été crée', self.tmpdirname)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LoaderCEN', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LoaderCEN/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'LoaderCEN'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&LoaderCEN'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def chargement_dalles_MNT(self):

        if self.dlg.comboBox.currentText() == "Choix du département":
            QMessageBox.question(self.iface.mainWindow(), u"Choix du département", u"Veuillez sélectionner un département afin de charger le dallage MNT 1 mètre associé !", QMessageBox.Ok)

        else:
            for lyr in QgsProject.instance().mapLayers().values():

                if lyr.name() == "dalles_MNT_1_m":
                    QgsProject.instance().removeMapLayers([lyr.id()])

        
            self.iface.addVectorLayer('https://sig.dsi-cen.org/qgis/downloads/dalles_mnt_1m/' + self.dlg.comboBox.currentText() + '.geojson', 'dalles_MNT_1_m', 'ogr')

    def chargement_dalles_orthos_50cm(self):

        self.iface.addVectorLayer('https://sig.dsi-cen.org/qgis/downloads/dalles_ortho_50cm.geojson', 'dalles_ortho_50cm', 'ogr')

        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == "dalles_ortho_20cm":
                QgsProject.instance().removeMapLayers([lyr.id()])

    def chargement_dalles_orthos_20cm(self):

        self.iface.addVectorLayer('https://sig.dsi-cen.org/qgis/downloads/dalles_ortho_20cm.geojson', 'dalles_ortho_20cm', 'ogr')

        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == "dalles_ortho_50cm":
                QgsProject.instance().removeMapLayers([lyr.id()])

    def chargement_MNT_1m(self):

        self.dlg.label_2.show()
        self.dlg.label_3.show()
        self.dlg.label_10.show()

        dossier_MNT = 'http://51.91.38.98/rgealti/'

        liste_couches = []

        if QgsProject.instance().mapLayersByName('dalles_MNT_1_m'):

            self.dalles_mnt = QgsProject.instance().mapLayersByName('dalles_MNT_1_m')[0]

            if len(self.dalles_mnt.selectedFeatures()) == 0:
                QMessageBox.question(self.iface.mainWindow(), u"Aucune dalle sélectionnée", u"Veuillez sélectionner une dalle depuis QGIS avant de tenter de charger le fichier associé !", QMessageBox.Ok)

            else:

                for f in self.dalles_mnt.selectedFeatures():
                    # refer to a specific values of a field index
                    NOM_COUCHE = f.attribute(0).replace('1-0_MNT_EXT', 'FXX').split('LAMB93_IGN69', 1)[0]+'MNT_LAMB93_IGN69'  # results in Group 1
                    liste_couches.append(NOM_COUCHE)

                if len(liste_couches) > 15:
                    self.QMBquestion = QMessageBox.question(iface.mainWindow(), u"Attention", "Pour des soucis de performances, le nombre de fichiers à charger en simultané est limité à 15.", QMessageBox.Ok)
                    if self.QMBquestion == QMessageBox.Ok:
                        print("Sélectionner moins de 15 dalles à la fois")

                else:
                    for couches in liste_couches:
                        alg_params = {
                            'DATA': '',
                            'METHOD': 0,  # GET
                            'OUTPUT': self.tmpdirname + str(couches),
                            'URL': dossier_MNT + str(couches) + '.asc'
                        }
                        processing.run('native:filedownloader', alg_params)
                        iface.addRasterLayer(self.tmpdirname + str(couches), str(couches))
                        print(couches)
        else:
            QMessageBox.question(self.iface.mainWindow(), u"Aucune couche 'dalles_MNT_1_m' détectée", u"Veuillez charger la couche 'dalles_MNT_1_m' depuis le menu 'choix des dalles' pour continuer.", QMessageBox.Ok)


        self.dlg.label_2.hide()
        self.dlg.label_3.hide()
        self.dlg.label_10.hide()


    def orthos(self):

        self.dlg.label_2.show()
        self.dlg.label_3.show()
        self.dlg.label_10.show()

        liste_couches = []

        if QgsProject.instance().mapLayersByName('dalles_ortho_50cm') or QgsProject.instance().mapLayersByName('dalles_ortho_20cm'):


            if QgsProject.instance().mapLayersByName('dalles_ortho_50cm'):
                self.dalles_ortho = QgsProject.instance().mapLayersByName('dalles_ortho_50cm')[0]
                dossier_orthos = 'http://51.91.38.98/bdortho/50cm/'
            elif QgsProject.instance().mapLayersByName('dalles_ortho_20cm'):
                self.dalles_ortho = QgsProject.instance().mapLayersByName('dalles_ortho_20cm')[0]
                dossier_orthos = 'http://51.91.38.98/bdortho/20cm/'


            if len(self.dalles_ortho.selectedFeatures()) == 0:
                QMessageBox.question(self.iface.mainWindow(), u"Aucune dalle sélectionnée", u"Veuillez sélectionner une dalle depuis QGIS avant de tenter de charger le fichier associé !", QMessageBox.Ok)

            else:

                for f in self.dalles_ortho.selectedFeatures():
                    # refer to a specific values of a field index
                    NOM_COUCHE = f.attribute(0)  # results in Group 1
                    NOM_COUCHE = NOM_COUCHE[2:]
                    liste_couches.append(NOM_COUCHE)

                if len(liste_couches) > 4:
                    self.QMBquestion = QMessageBox.question(iface.mainWindow(), u"Attention", "Pour des soucis de performances, le nombre de fichiers à charger en simultané est limité à 4.", QMessageBox.Ok)
                    if self.QMBquestion == QMessageBox.Ok:
                        print("Sélectionner moins de 15 dalles à la fois")

                else:

                    for couches in liste_couches:
                        alg_params = {
                            'DATA': '',
                            'METHOD': 0,  # GET
                            'OUTPUT': self.tmpdirname + str(couches),
                            'URL': dossier_orthos + str(couches)
                        }
                        processing.run('native:filedownloader', alg_params)

                        iface.addRasterLayer(self.tmpdirname + str(couches), str(couches))
                        print(couches)

                    print("TADAM")
        else:
            QMessageBox.question(self.iface.mainWindow(), u"Aucune couche 'dalles_ortho' détectée", u"Veuillez sélectionner l'une des deux couches 'dalles_orthos' dans le menu 'choix des dalles' pour continuer.", QMessageBox.Ok)

        self.dlg.label_2.hide()
        self.dlg.label_3.hide()
        self.dlg.label_10.hide()


    def chargement_cadastre(self):

        self.dlg.label_2.show()
        self.dlg.label_3.show()
        self.dlg.label_10.show()

        numero_dept = self.dlg.lineEdit.text()[:2]

        uri = "https://opendata.cen-nouvelle-aquitaine.org/administratif/wfs?VERSION=1.0.0&TYPENAME=administratif:parcelle_", numero_dept, "&SRSNAME=EPSG:4326&request=GetFeature&cql_filter=commune='", self.dlg.lineEdit.text(), "'"
        uri = "".join(uri)

        cadastre = QgsVectorLayer(uri, self.dlg.lineEdit.text(), "WFS")

        QgsProject.instance().addMapLayer(cadastre)

        nom_couche = "parcelles_cadastrales_commune_" + self.dlg.lineEdit.text()

        cadastre.setName(nom_couche)
        print(cadastre.extent())
        # Find out if we need to transform coordinates
        proj = QgsProject.instance()
        if cadastre.crs().authid() != proj.crs().authid():
            print("La couche 'cadastre' et le projet QGIS ne partagent pas le même CRS",
                  cadastre.crs().authid(),
                  proj.crs().authid()
                  )
            tr = QgsCoordinateTransform(cadastre.crs(), proj.crs(), proj)
            ex = tr.transform(cadastre.extent())

            iface.mapCanvas().setExtent(ex)
            iface.mapCanvas().refresh()
        else:
            iface.mapCanvas().setExtent(cadastre.extent())


        iface.mapCanvas().refresh()

        # if cadastre.featureCount() == 0:
        #     print(cadastre.featureCount())
        #     QMessageBox.question(self.iface.mainWindow(), u"Couche vide", u"Code Insee inconnu ! ", QMessageBox.Ok)

        # layermap = proj.mapLayers()
        # RemoveLayers = []
        # for name, layer in layermap.items():
        #     if layer.isValid():
        #         if layer.type() == QgsMapLayer.VectorLayer:
        #             if layer.featureCount() == 0:
        #                 RemoveLayers.append(layer.id())
        # if len(RemoveLayers) > 0:
        #     proj.instance().removeMapLayers(RemoveLayers)


        self.dlg.label_2.hide()
        self.dlg.label_3.hide()
        self.dlg.label_10.hide()


    def popup(self):

        self.dialog = Popup()  # +++ - self
        self.dialog.text_edit.show()