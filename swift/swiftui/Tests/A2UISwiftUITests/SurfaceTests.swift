// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import A2UICore
import A2UIJSON
import A2UISwiftUI
import BasicCatalog
import BasicCatalogSwiftUI
import JSONSchema
import OrderedJSON
import SwiftUI
import Testing

#if canImport(AppKit)
  import AppKit
#elseif canImport(UIKit)
  import UIKit
#endif

private func makeTestSurfaceCatalogForRendering() throws -> AnyCatalog {
  let textSchema = try Schema(
    instance: """
      {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "component": { "type": "string" },
          "text": { "$ref": "https://a2ui.org/schemas/v0_9_1/common.json#/$defs/DynamicString" }
        },
        "required": ["id", "component"]
      }
      """,
    remoteSchemas: A2UICommonSchema.allSchemas
  )
  return Catalog(
    id: "default",
    components: [
      AnyComponentAPI(
        name: "text",
        schema: textSchema
      )
    ]
  )
}

@MainActor
struct SurfaceTests {

  @Test func surfaceInitializesWithViewModel() throws {
    let catalog = try makeTestSurfaceCatalogForRendering()
    let viewModel = SurfaceViewModel(
      surfaceID: "s1",
      catalog: catalog
    )
    let surface = Surface(
      viewModel: viewModel
    )
    #expect(surface.surfaceID == "s1")
  }

  @Test func surfaceIDMatchesViewModel() throws {
    let catalog = try makeTestSurfaceCatalogForRendering()
    let viewModel = SurfaceViewModel(
      surfaceID: "s1",
      catalog: catalog
    )
    let firstSurface = Surface(
      viewModel: viewModel
    )
    let secondSurface = Surface(
      viewModel: viewModel
    )
    #expect(firstSurface.surfaceID == secondSurface.surfaceID)
  }

  @Test func surfaceDifferentSurfaceIDs() throws {
    let catalog = try makeTestSurfaceCatalogForRendering()
    let firstViewModel = SurfaceViewModel(
      surfaceID: "s1",
      catalog: catalog
    )
    let secondViewModel = SurfaceViewModel(
      surfaceID: "s2",
      catalog: catalog
    )
    let firstSurface = Surface(
      viewModel: firstViewModel
    )
    let secondSurface = Surface(
      viewModel: secondViewModel
    )
    #expect(firstSurface.surfaceID != secondSurface.surfaceID)
  }

  @Test func surfaceViewModelMetadataMutatorsExposeExtensions() throws {
    let catalog = try makeTestSurfaceCatalogForRendering()
    let viewModel = SurfaceViewModel(
      surfaceID: "s1",
      catalog: catalog,
      metadata: ["extensions": .object(["surfaceTheme": .string("dark")])]
    )
    #expect(viewModel.extensions == ["surfaceTheme": .string("dark")])
    try viewModel.setExtension("mode", value: .string("compact"))
    #expect(
      viewModel.extensions == [
        "surfaceTheme": .string("dark"),
        "mode": .string("compact"),
      ]
    )
    viewModel.removeExtension("surfaceTheme")
    viewModel.removeExtension("mode")
    #expect(viewModel.metadata == nil)
  }

  @Test func swappingSurfaceViewModelsDisposesOldResolverAndRendersNewSurface() throws {
    let coreCatalog = BasicCatalog.makeCatalog(version: .v091)
    let swiftUICatalog = BasicCatalogImplementation.makeCatalog(version: .v091)

    let firstViewModel = SurfaceViewModel(surfaceID: "surface-a", catalog: coreCatalog)
    firstViewModel.componentsModel.addComponent(
      ComponentModel(
        id: "root",
        type: "Text",
        properties: ["text": .string("Surface A")]
      )
    )
    let secondViewModel = SurfaceViewModel(surfaceID: "surface-b", catalog: coreCatalog)
    secondViewModel.componentsModel.addComponent(
      ComponentModel(
        id: "root",
        type: "Text",
        properties: ["text": .string("Surface B")]
      )
    )

    let firstSurface = Surface(viewModel: firstViewModel, catalog: swiftUICatalog)
    #if canImport(AppKit)
      let hostingView = NSHostingView(rootView: firstSurface)
      hostingView.frame = NSRect(x: 0, y: 0, width: 320, height: 120)
      hostingView.layoutSubtreeIfNeeded()
    #elseif canImport(UIKit)
      let hostingController = UIHostingController(rootView: firstSurface)
      hostingController.view.frame = CGRect(x: 0, y: 0, width: 320, height: 120)
      hostingController.view.layoutIfNeeded()
    #endif

    #expect(firstViewModel.rootNode?.string(for: "text") == "Surface A")

    // Swap to the second surface model and dispose the first surface model.
    firstViewModel.dispose()
    let secondSurface = Surface(viewModel: secondViewModel, catalog: swiftUICatalog)
    #if canImport(AppKit)
      hostingView.rootView = secondSurface
      hostingView.layoutSubtreeIfNeeded()
    #elseif canImport(UIKit)
      hostingController.rootView = secondSurface
      hostingController.view.layoutIfNeeded()
    #endif

    // Mutations to the disposed first surface no longer resolve new nodes.
    firstViewModel.componentsModel.addComponent(
      ComponentModel(
        id: "root",
        type: "Text",
        properties: ["text": .string("Stale Update")]
      )
    )
    #expect(firstViewModel.rootNode?.string(for: "text") == "Surface A")
    #expect(secondSurface.surfaceID == "surface-b")
    #expect(secondViewModel.rootNode?.string(for: "text") == "Surface B")
  }
}
