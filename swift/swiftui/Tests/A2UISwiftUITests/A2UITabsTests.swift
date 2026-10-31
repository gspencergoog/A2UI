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
import A2UISwiftUI
import BasicCatalog
import BasicCatalogSwiftUI
import Foundation
import OrderedJSON
import SwiftUI
import Testing

@MainActor
struct A2UITabsTests {

  @Test func resolvesTabTitlesFromBindingsAndSelectsFirstTabContent() {
    let firstChild = Node(id: "tab1_body", type: "Text", properties: ["text": "Overview body"])
    let secondChild = Node(id: "tab2_body", type: "Text", properties: ["text": "Details body"])

    let firstTab = ResolvedDictionary([
      "title": DataBinding<String>(
        identity: .path("/tabs/first"),
        value: "Overview",
        set: { _ in }
      ),
      "child": firstChild,
    ])
    let secondTab = ResolvedDictionary([
      "title": DataBinding<String>(
        identity: .path("/tabs/second"),
        value: "Details",
        set: { _ in }
      ),
      "child": secondChild,
    ])

    let tabsNode = Node(
      id: "tabs1",
      type: "Tabs",
      properties: [
        "tabs": ResolvedArray([firstTab, secondTab])
      ]
    )

    let view = A2UITabs(node: tabsNode)
    var extractedTabs: [(id: Int, title: String, childID: String?)] = []
    extractTabs(from: view.body, into: &extractedTabs)

    #expect(extractedTabs.map(\.title) == ["Overview", "Details"])
    #expect(extractedTabs.map(\.childID) == ["tab1_body", "tab2_body"])

    var renderedChildIDs: [String] = []
    collectComponentNodeIDs(in: view.body, into: &renderedChildIDs)
    #expect(renderedChildIDs == ["tab1_body"])
  }

  @Test func boundTabTitlesUpdateWithDataModelAndActiveChildFollowsTabOrder() async throws {
    let processor = MessageProcessor(catalogs: [V10BasicCatalog.catalog])
    let parser = MessageParser()
    let initialMessages: [[String: Any]] = [
      [
        "version": "1.0",
        "createSurface": [
          "surfaceId": "tabs-surface",
          "catalogId": V10BasicCatalog.catalogURI,
        ],
      ],
      [
        "version": "1.0",
        "updateComponents": [
          "surfaceId": "tabs-surface",
          "components": [
            [
              "id": "root",
              "component": "Tabs",
              "tabs": [
                ["title": ["@path": "/firstTitle"], "child": "pane_a"],
                ["title": ["@path": "/secondTitle"], "child": "pane_b"],
              ],
            ],
            ["id": "pane_a", "component": "Text", "text": "Pane A"],
            ["id": "pane_b", "component": "Text", "text": "Pane B"],
          ],
        ],
      ],
      [
        "version": "1.0",
        "updateDataModel": [
          "surfaceId": "tabs-surface",
          "value": ["firstTitle": "Summary", "secondTitle": "Metrics"],
        ],
      ],
    ]

    for message in initialMessages {
      let data = try JSONSerialization.data(withJSONObject: message)
      processor.process(message: try parser.decode(jsonData: data))
    }
    await Task.yield()

    let surface = try #require(processor.surfaceGroupModel.surfacesMap["tabs-surface"])
    let rootBefore = try #require(surface.rootNode)
    let viewBefore = A2UITabs(node: rootBefore)

    var tabsBefore: [(id: Int, title: String, childID: String?)] = []
    extractTabs(from: viewBefore.body, into: &tabsBefore)
    #expect(tabsBefore.map(\.title) == ["Summary", "Metrics"])

    var activeBefore: [String] = []
    collectComponentNodeIDs(in: viewBefore.body, into: &activeBefore)
    #expect(activeBefore == ["pane_a"])

    // Update the bound title and swap the active first tab to pane_b.
    let updateMessages: [[String: Any]] = [
      [
        "version": "1.0",
        "updateDataModel": [
          "surfaceId": "tabs-surface",
          "path": "/firstTitle",
          "value": "Updated Summary",
        ],
      ],
      [
        "version": "1.0",
        "updateComponents": [
          "surfaceId": "tabs-surface",
          "components": [
            [
              "id": "root",
              "component": "Tabs",
              "tabs": [
                ["title": ["@path": "/secondTitle"], "child": "pane_b"],
                ["title": ["@path": "/firstTitle"], "child": "pane_a"],
              ],
            ]
          ],
        ],
      ],
    ]
    for message in updateMessages {
      let data = try JSONSerialization.data(withJSONObject: message)
      processor.process(message: try parser.decode(jsonData: data))
    }
    await Task.yield()

    let rootAfter = try #require(surface.rootNode)
    let viewAfter = A2UITabs(node: rootAfter)

    var tabsAfter: [(id: Int, title: String, childID: String?)] = []
    extractTabs(from: viewAfter.body, into: &tabsAfter)
    #expect(tabsAfter.map(\.title) == ["Metrics", "Updated Summary"])

    var activeAfter: [String] = []
    collectComponentNodeIDs(in: viewAfter.body, into: &activeAfter)
    #expect(activeAfter == ["pane_b"])
  }

  @Test func tabsRenderFromCatalogs() throws {
    for version in [A2UIProtocolVersion.v091, .v10] {
      let catalog = BasicCatalogImplementation.makeCatalog(version: version)
      let child = Node(id: "tab_child", type: "Text", properties: ["text": "Body"])
      let node = Node(
        id: "tabsCatalog_\(version.rawValue)",
        type: "Tabs",
        catalogID: catalog.id,
        properties: [
          "tabs": ResolvedArray([
            ResolvedDictionary(["title": "First", "child": child])
          ])
        ]
      )
      let rendered = Surface.render(node: node, using: [catalog.id: catalog])
      #expect(rendered != nil)
    }
  }

  private func extractTabs(
    from value: Any,
    into results: inout [(id: Int, title: String, childID: String?)]
  ) {
    let mirror = Mirror(reflecting: value)
    var id: Int?
    var title: String?
    var hasChildNodeKey = false
    var childID: String?
    for child in mirror.children {
      switch child.label {
      case "id":
        id = child.value as? Int
      case "title":
        title = child.value as? String
      case "childNode":
        hasChildNodeKey = true
        childID = (child.value as? Node)?.id
      default:
        break
      }
    }
    if let id, let title, hasChildNodeKey {
      results.append((id: id, title: title, childID: childID))
      return
    }
    for child in mirror.children {
      extractTabs(from: child.value, into: &results)
    }
  }

  private func collectComponentNodeIDs(in value: Any, into ids: inout [String]) {
    if let nodeView = value as? ComponentNodeView {
      ids.append(nodeView.node.id)
      return
    }
    for child in Mirror(reflecting: value).children {
      collectComponentNodeIDs(in: child.value, into: &ids)
    }
  }
}
