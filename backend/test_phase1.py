"""
Test script for Phase 1 - Core Infrastructure
Tests all managers and models
"""

import os
import sys
import pandas as pd
import shutil
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.project_manager import ProjectManager
from src.version_manager import VersionManager
from src.state_manager import StateManager
from src.models import Project, Chat, Message, Version, AppConfig


def cleanup_test_data():
    """Remove test data directory"""
    test_dir = "data_test"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print("✓ Cleaned up test directory")


def test_models():
    """Test data models and serialization"""
    print("\n=== Testing Models ===")

    # Test Project
    project = Project.create_new(
        name="Test Project",
        filename="test.csv",
        rows=100,
        cols=5,
        size_mb=0.5
    )
    project_dict = project.to_dict()
    project_restored = Project.from_dict(project_dict)
    assert project_restored.name == "Test Project"
    assert project_restored.total_rows == 100
    print("✓ Project model works")

    # Test Chat
    chat = Chat.create_new(project_id=project.id, name="Test Chat")
    chat_dict = chat.to_dict()
    chat_restored = Chat.from_dict(chat_dict)
    assert chat_restored.name == "Test Chat"
    assert chat_restored.project_id == project.id
    print("✓ Chat model works")

    # Test Message
    msg = Message.create_user_message(chat_id=chat.id, content="Hello")
    msg_dict = msg.to_dict()
    msg_restored = Message.from_dict(msg_dict)
    assert msg_restored.content == "Hello"
    assert msg_restored.role == "user"
    print("✓ Message model works")

    # Test Version
    version = Version.create_new(
        version_number=1,
        project_id=project.id,
        file_path="versions/v1.csv",
        file_size_mb=0.5,
        change_description="Initial",
        row_count=100,
        column_count=5
    )
    version_dict = version.to_dict()
    version_restored = Version.from_dict(version_dict)
    assert version_restored.version_number == 1
    assert version_restored.change_description == "Initial"
    print("✓ Version model works")

    # Test AppConfig
    config = AppConfig.create_default()
    config_dict = config.to_dict()
    config_restored = AppConfig.from_dict(config_dict)
    assert config_restored.version == "2.0.0"
    assert config_restored.judge_enabled == True
    print("✓ AppConfig model works")


def test_state_manager():
    """Test StateManager persistence"""
    print("\n=== Testing StateManager ===")

    state = StateManager("data_test")

    # Test config save/load
    config = AppConfig.create_default()
    config.last_active_project_id = "test-123"
    state.save_config(config)
    loaded_config = state.load_config()
    assert loaded_config.last_active_project_id == "test-123"
    print("✓ Config save/load works")

    # Test project metadata save/load
    project = Project.create_new(
        name="Sales Data",
        filename="sales.csv",
        rows=1000,
        cols=10,
        size_mb=2.5
    )
    state.save_project_metadata(project)
    loaded_project = state.load_project_metadata(project.id)
    assert loaded_project.name == "Sales Data"
    assert loaded_project.total_rows == 1000
    print("✓ Project metadata save/load works")

    # Test chat save/load
    chat = Chat.create_new(project_id=project.id, name="Analysis Chat")
    msg1 = Message.create_user_message(chat_id=chat.id, content="Show me sales")
    msg2 = Message.create_assistant_message(
        chat_id=chat.id,
        content="Here are the sales",
        code="df.head()",
        output_type="table"
    )
    messages = [msg1, msg2]

    state.save_chat(chat, messages)
    loaded_chat, loaded_messages = state.load_chat(project.id, chat.id)
    assert loaded_chat.name == "Analysis Chat"
    assert len(loaded_messages) == 2
    assert loaded_messages[0].content == "Show me sales"
    print("✓ Chat save/load works")

    # Test list operations
    project_ids = state.list_project_ids()
    assert project.id in project_ids
    print("✓ List project IDs works")

    all_projects = state.load_all_projects()
    assert len(all_projects) >= 1
    print("✓ Load all projects works")


def test_version_manager():
    """Test VersionManager"""
    print("\n=== Testing VersionManager ===")

    vm = VersionManager("data_test")

    # Create test project
    project_id = "test-project-123"

    # Create initial version
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'SF']
    })

    version1 = vm.create_initial_version(
        project_id=project_id,
        csv_dataframe=df1,
        original_filename="users.csv"
    )
    assert version1 is not None
    assert version1.version_number == 1
    print("✓ Initial version created")

    # Load version
    loaded_df1 = vm.load_version_dataframe(project_id, 1)
    assert loaded_df1 is not None
    assert len(loaded_df1) == 3
    assert 'name' in loaded_df1.columns
    print("✓ Load version dataframe works")

    # Create new version (modified data)
    df2 = df1.copy()
    df2['salary'] = [50000, 60000, 70000]

    version2 = vm.create_new_version(
        project_id=project_id,
        csv_dataframe=df2,
        change_description="Added salary column"
    )
    assert version2 is not None
    assert version2.version_number == 2
    assert "Added" in version2.change_description or "salary" in version2.change_description
    print("✓ New version created with auto-detection")

    # Get version history
    versions = vm.get_version_history(project_id)
    assert len(versions) == 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2
    print("✓ Version history works")

    # Load current dataframe
    current_df = vm.load_current_dataframe(project_id)
    assert current_df is not None
    assert 'salary' in current_df.columns
    print("✓ Load current dataframe works")

    # Revert to version 1
    version3 = vm.revert_to_version(project_id, 1)
    assert version3 is not None
    assert version3.version_number == 3
    assert "Reverted" in version3.change_description
    print("✓ Revert to version works")

    # Verify revert worked
    current_df_after_revert = vm.load_current_dataframe(project_id)
    assert 'salary' not in current_df_after_revert.columns
    print("✓ Revert correctly restored old data")

    # Get stats
    stats = vm.get_version_stats(project_id)
    assert stats['version_count'] == 3
    print("✓ Version stats works")


def test_project_manager():
    """Test ProjectManager (high-level)"""
    print("\n=== Testing ProjectManager ===")

    pm = ProjectManager("data_test")

    # Create project
    df = pd.DataFrame({
        'product': ['Widget A', 'Widget B', 'Widget C'],
        'price': [10.99, 15.99, 20.99],
        'stock': [100, 50, 25]
    })

    project = pm.create_project(
        csv_dataframe=df,
        original_filename="products.csv",
        project_name="Product Inventory"
    )
    assert project is not None
    assert project.name == "Product Inventory"
    assert project.current_version == 1
    assert len(project.chat_ids) == 1  # Default chat created
    print("✓ Create project works (with version + default chat)")

    # Get project
    loaded_project = pm.get_project(project.id)
    assert loaded_project is not None
    assert loaded_project.name == "Product Inventory"
    print("✓ Get project works")

    # Get project with dataframe
    result = pm.get_project_with_dataframe(project.id)
    assert result is not None
    proj, df_loaded = result
    assert proj.id == project.id
    assert len(df_loaded) == 3
    print("✓ Get project with dataframe works")

    # List all projects
    all_projects = pm.list_all_projects()
    assert len(all_projects) >= 1
    print("✓ List all projects works")

    # Update project
    updated = pm.rename_project(project.id, "Updated Inventory")
    assert updated is not None
    assert updated.name == "Updated Inventory"
    print("✓ Rename project works")

    # Get stats
    stats = pm.get_project_stats(project.id)
    assert stats['project_name'] == "Updated Inventory"
    assert stats['rows'] == 3
    assert stats['columns'] == 3
    print("✓ Project stats works")

    # Search projects
    results = pm.search_projects("inventory")
    assert len(results) >= 1
    print("✓ Search projects works")


def test_integration():
    """Test integrated workflow"""
    print("\n=== Testing Integrated Workflow ===")

    pm = ProjectManager("data_test")
    vm = VersionManager("data_test")
    sm = StateManager("data_test")

    # 1. Create project
    df = pd.DataFrame({
        'customer': ['John', 'Jane', 'Bob'],
        'revenue': [1000, 2000, 1500]
    })

    project = pm.create_project(df, "customers.csv", "Customer Revenue")
    print("✓ Created project")

    # 2. Modify DataFrame and create new version
    df_modified = df.copy()
    df_modified['profit'] = [100, 200, 150]

    new_version = vm.create_new_version(
        project_id=project.id,
        csv_dataframe=df_modified,
        change_description="Added profit column"
    )
    assert new_version.version_number == 2
    print("✓ Created new version")

    # 3. Refresh project stats
    refreshed = pm.refresh_project_stats(project.id)
    assert refreshed.current_version == 2
    assert refreshed.total_columns == 3  # Now has profit column
    print("✓ Refreshed project stats")

    # 4. Create additional chat
    chat2 = Chat.create_new(project.id, "Second Chat")
    sm.save_chat(chat2, [])
    pm.add_chat_to_project(project.id, chat2.id)

    updated_project = pm.get_project(project.id)
    assert len(updated_project.chat_ids) == 2
    print("✓ Added second chat to project")

    # 5. Set active chat
    pm.set_active_chat(project.id, chat2.id)
    active_chat_id = pm.get_active_chat_id(project.id)
    assert active_chat_id == chat2.id
    print("✓ Set active chat")

    # 6. Get all stats
    all_stats = pm.get_all_stats()
    assert all_stats['total_projects'] >= 1
    assert all_stats['total_chats'] >= 2
    print("✓ Got comprehensive stats")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 1 - CORE INFRASTRUCTURE TESTS")
    print("=" * 60)

    # Cleanup before tests
    cleanup_test_data()

    try:
        test_models()
        test_state_manager()
        test_version_manager()
        test_project_manager()
        test_integration()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nPhase 1 implementation is complete and working correctly.")
        print("Ready to proceed to Phase 2 (Multi-Chat Support).")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup after tests
        print("\nCleaning up test data...")
        cleanup_test_data()


if __name__ == "__main__":
    run_all_tests()
